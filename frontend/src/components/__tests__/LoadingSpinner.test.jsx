import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Spinner, { 
  LogoSpinner, 
  FullPageLoader, 
  ButtonSpinner,
  CircularProgress,
  LoadingOverlay,
  WaveLoader 
} from '../LoadingSpinner';

describe('Spinner Component', () => {
  it('should render spinner with default props', () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector('svg');
    
    expect(spinner).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('w-6', 'h-6', 'text-primary-500');
  });

  it('should render with different sizes', () => {
    const { container: smallContainer } = render(<Spinner size="sm" />);
    expect(smallContainer.firstChild).toHaveClass('w-4', 'h-4');

    const { container: largeContainer } = render(<Spinner size="lg" />);
    expect(largeContainer.firstChild).toHaveClass('w-8', 'h-8');
  });

  it('should render with different colors', () => {
    const { container: whiteContainer } = render(<Spinner color="white" />);
    expect(whiteContainer.firstChild).toHaveClass('text-white');

    const { container: grayContainer } = render(<Spinner color="gray" />);
    expect(grayContainer.firstChild).toHaveClass('text-gray-500');
  });

  it('should apply custom className', () => {
    const { container } = render(<Spinner className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('LogoSpinner Component', () => {
  it('should render logo spinner with default props', () => {
    render(<LogoSpinner />);
    
    expect(screen.getByText('P')).toBeInTheDocument(); // Logo icon
  });

  it('should render with message', () => {
    const message = 'Loading data...';
    render(<LogoSpinner message={message} />);
    
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  it('should render with different sizes', () => {
    const { rerender } = render(<LogoSpinner size="sm" />);
    expect(screen.getByText('P')).toBeInTheDocument();

    rerender(<LogoSpinner size="lg" />);
    expect(screen.getByText('P')).toBeInTheDocument();
  });

  it('should render animated dots', () => {
    const { container } = render(<LogoSpinner />);
    const dots = container.querySelectorAll('.bg-primary-500.rounded-full');
    
    expect(dots).toHaveLength(3);
  });
});

describe('FullPageLoader Component', () => {
  it('should render full page loader', () => {
    render(<FullPageLoader />);
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
    expect(screen.getByText('P')).toBeInTheDocument(); // Logo
  });

  it('should render with custom message', () => {
    const customMessage = 'Processing...';
    render(<FullPageLoader message={customMessage} />);
    
    expect(screen.getByText(customMessage)).toBeInTheDocument();
  });

  it('should have fixed positioning and backdrop', () => {
    const { container } = render(<FullPageLoader />);
    const overlay = container.firstChild;
    
    expect(overlay).toHaveClass('fixed', 'inset-0', 'bg-white', 'bg-opacity-90', 'backdrop-blur-sm', 'z-50');
  });
});

describe('ButtonSpinner Component', () => {
  it('should render button spinner', () => {
    const { container } = render(<ButtonSpinner />);
    const spinner = container.querySelector('svg');
    
    expect(spinner).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('animate-spin');
  });

  it('should render with different sizes', () => {
    const { container } = render(<ButtonSpinner size="lg" />);
    expect(container.firstChild).toHaveClass('w-8', 'h-8');
  });

  it('should use current color', () => {
    const { container } = render(<ButtonSpinner />);
    expect(container.firstChild).toHaveClass('text-current');
  });
});

describe('CircularProgress Component', () => {
  it('should render circular progress with default props', () => {
    const { container } = render(<CircularProgress />);
    const svg = container.querySelector('svg');
    const circles = container.querySelectorAll('circle');
    
    expect(svg).toBeInTheDocument();
    expect(circles).toHaveLength(2); // Background and progress circles
  });

  it('should show percentage by default', () => {
    render(<CircularProgress progress={75} />);
    
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should hide percentage when showPercentage is false', () => {
    render(<CircularProgress progress={75} showPercentage={false} />);
    
    expect(screen.queryByText('75%')).not.toBeInTheDocument();
  });

  it('should render with different sizes', () => {
    const { container: smallContainer } = render(<CircularProgress size="sm" />);
    const smallSvg = smallContainer.querySelector('svg');
    expect(smallSvg).toHaveAttribute('width', '40');

    const { container: largeContainer } = render(<CircularProgress size="lg" />);
    const largeSvg = largeContainer.querySelector('svg');
    expect(largeSvg).toHaveAttribute('width', '80');
  });

  it('should handle progress values correctly', () => {
    render(<CircularProgress progress={50} />);
    expect(screen.getByText('50%')).toBeInTheDocument();

    render(<CircularProgress progress={100} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});

describe('LoadingOverlay Component', () => {
  it('should render when show is true', () => {
    render(<LoadingOverlay show={true} />);
    
    const overlay = document.querySelector('.absolute.inset-0');
    expect(overlay).toBeInTheDocument();
  });

  it('should not render when show is false', () => {
    render(<LoadingOverlay show={false} />);
    
    const overlay = document.querySelector('.absolute.inset-0');
    expect(overlay).not.toBeInTheDocument();
  });

  it('should render with message', () => {
    const message = 'Loading content...';
    render(<LoadingOverlay show={true} message={message} />);
    
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  it('should apply blur when blur prop is true', () => {
    const { container } = render(<LoadingOverlay show={true} blur={true} />);
    const overlay = container.firstChild;
    
    expect(overlay).toHaveClass('backdrop-blur-sm');
  });

  it('should not apply blur when blur prop is false', () => {
    const { container } = render(<LoadingOverlay show={true} blur={false} />);
    const overlay = container.firstChild;
    
    expect(overlay).not.toHaveClass('backdrop-blur-sm');
  });
});

describe('WaveLoader Component', () => {
  it('should render wave loader', () => {
    const { container } = render(<WaveLoader />);
    const waves = container.querySelectorAll('.bg-primary-500.rounded-full');
    
    expect(waves).toHaveLength(5);
  });

  it('should apply custom className', () => {
    const { container } = render(<WaveLoader className="custom-wave" />);
    
    expect(container.firstChild).toHaveClass('custom-wave');
  });

  it('should have proper structure', () => {
    const { container } = render(<WaveLoader />);
    const wrapper = container.firstChild;
    
    expect(wrapper).toHaveClass('flex', 'items-center', 'justify-center', 'space-x-1');
  });
});