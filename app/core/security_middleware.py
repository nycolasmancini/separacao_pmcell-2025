"""
Security middleware for rate limiting and security headers
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# In-memory rate limiting store (use Redis in production)
_rate_limit_store: Dict[str, list] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many requests.",
                headers={"Retry-After": str(self.period)}
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        
        # Clean old entries
        _rate_limit_store[client_ip] = [
            timestamp for timestamp in _rate_limit_store[client_ip]
            if current_time - timestamp < self.period
        ]
        
        # Check if limit exceeded
        if len(_rate_limit_store[client_ip]) >= self.calls:
            return False
        
        # Add current request
        _rate_limit_store[client_ip].append(current_time)
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
        }
        
        # Add HSTS in production with HTTPS
        if settings.ENVIRONMENT == "production":
            security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        security_headers["Content-Security-Policy"] = csp_policy
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware for security monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} [{user_agent[:100]}]"
        )
        
        # Detect suspicious patterns
        self._detect_suspicious_activity(request, client_ip)
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"Response: {response.status_code} "
                f"in {process_time:.4f}s"
            )
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"from {client_ip} in {process_time:.4f}s - {str(e)}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _detect_suspicious_activity(self, request: Request, client_ip: str):
        """Detect and log suspicious activity"""
        suspicious_patterns = [
            "script", "javascript:", "vbscript:", "<script",
            "union select", "drop table", "insert into",
            "delete from", "update set", "--", "/*", "*/"
        ]
        
        # Check URL and query parameters
        full_url = str(request.url)
        for pattern in suspicious_patterns:
            if pattern.lower() in full_url.lower():
                logger.warning(
                    f"Suspicious request detected from {client_ip}: "
                    f"Pattern '{pattern}' in URL {full_url}"
                )
                break
        
        # Check User-Agent for known bot patterns
        user_agent = request.headers.get("User-Agent", "").lower()
        bot_patterns = ["bot", "crawler", "spider", "scraper"]
        
        if any(pattern in user_agent for pattern in bot_patterns):
            logger.info(f"Bot detected from {client_ip}: {user_agent}")


# Security utility functions
def generate_secure_key(length: int = 32) -> str:
    """Generate a secure random key"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """Hash password securely"""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "\"", "'", "&", "javascript:", "vbscript:"]
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


def validate_jwt_secret(secret: str) -> bool:
    """Validate JWT secret strength"""
    if len(secret) < 32:
        return False
    
    has_upper = any(c.isupper() for c in secret)
    has_lower = any(c.islower() for c in secret)
    has_digit = any(c.isdigit() for c in secret)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in secret)
    
    return all([has_upper, has_lower, has_digit, has_special])


# Configuration validation
def validate_security_config():
    """Validate security configuration on startup"""
    errors = []
    
    # Check JWT secret strength
    if not validate_jwt_secret(settings.SECRET_KEY):
        errors.append(
            "JWT SECRET_KEY is weak. Use at least 32 characters with "
            "uppercase, lowercase, digits, and special characters."
        )
    
    # Check production settings
    if settings.ENVIRONMENT == "production":
        if settings.DEBUG:
            errors.append("DEBUG should be False in production")
        
        if "localhost" in str(settings.get_cors_origins()):
            errors.append("CORS origins should not include localhost in production")
    
    if errors:
        logger.error("Security configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        
        if settings.ENVIRONMENT == "production" and not settings.SKIP_SECURITY_VALIDATION:
            raise RuntimeError("Security configuration is invalid for production")
    else:
        logger.info("Security configuration validated successfully")