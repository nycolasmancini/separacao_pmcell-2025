"""
Testes de integração para endpoints de pedidos.
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.models.order import Order
from app.core.security import create_access_token


class TestOrdersAPI:
    """Testes de integração para a API de pedidos."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Usuário de teste."""
        user = User(
            name="Test User",
            pin="1234",
            role="admin"
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    @pytest.fixture
    async def auth_headers(self, test_user):
        """Headers de autenticação."""
        user = await test_user
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Caminho para PDF de exemplo."""
        return Path(__file__).parent.parent / "fixtures" / "pdfs" / "sample_order.pdf"
    
    async def test_upload_pdf_success(self, client, auth_headers, sample_pdf_path):
        """Testa upload de PDF com sucesso."""
        headers = await auth_headers
        with open(sample_pdf_path, "rb") as pdf_file:
            response = client.post(
                "/api/v1/orders/upload",
                headers=auth_headers,
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={
                    "logistics_type": "lalamove",
                    "package_type": "caixa",
                    "observations": "Teste de upload"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "PDF processado com sucesso"
        assert data["data"] is not None
        assert data["errors"] is None
        
        # Verificar dados extraídos
        pdf_data = data["data"]
        assert pdf_data["order_number"] == "12345"
        assert pdf_data["client_name"] == "EMPRESA TESTE LTDA"
        assert pdf_data["seller_name"] == "João Silva"
        assert pdf_data["total_value"] == 1250.0
        assert len(pdf_data["items"]) == 2
    
    def test_upload_pdf_invalid_file_type(self, client, auth_headers):
        """Testa upload de arquivo não-PDF."""
        response = client.post(
            "/api/v1/orders/upload",
            headers=auth_headers,
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]
    
    def test_upload_pdf_no_file(self, client, auth_headers):
        """Testa upload sem arquivo."""
        response = client.post(
            "/api/v1/orders/upload",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_pdf_unauthenticated(self, client, sample_pdf_path):
        """Testa upload sem autenticação."""
        with open(sample_pdf_path, "rb") as pdf_file:
            response = client.post(
                "/api/v1/orders/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")}
            )
        
        assert response.status_code == 401
    
    def test_confirm_order_success(self, client, auth_headers):
        """Testa confirmação de pedido com sucesso."""
        order_data = {
            "pdf_data": {
                "order_number": "12345",
                "client_name": "EMPRESA TESTE LTDA",
                "seller_name": "João Silva",
                "order_date": "2024-07-12T00:00:00",
                "total_value": 1250.0,
                "items": [
                    {
                        "product_code": "001",
                        "product_reference": "REF-001",
                        "product_name": "PRODUTO TESTE 1",
                        "quantity": 5,
                        "unit_price": 100.0,
                        "total_price": 500.0
                    },
                    {
                        "product_code": "002",
                        "product_reference": "REF-002",
                        "product_name": "PRODUTO TESTE 2",
                        "quantity": 3,
                        "unit_price": 250.0,
                        "total_price": 750.0
                    }
                ]
            },
            "logistics_type": "lalamove",
            "package_type": "caixa",
            "observations": "Teste de confirmação"
        }
        
        response = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["order_number"] == "12345"
        assert data["client_name"] == "EMPRESA TESTE LTDA"
        assert data["seller_name"] == "João Silva"
        assert data["total_value"] == 1250.0
        assert data["items_count"] == 8  # 5 + 3
        assert data["progress_percentage"] == 0.0
        assert "id" in data
    
    def test_confirm_order_duplicate(self, client, auth_headers):
        """Testa confirmação de pedido duplicado."""
        order_data = {
            "pdf_data": {
                "order_number": "12345",
                "client_name": "EMPRESA TESTE LTDA",
                "seller_name": "João Silva",
                "order_date": "2024-07-12T00:00:00",
                "total_value": 1250.0,
                "items": [
                    {
                        "product_code": "001",
                        "product_reference": "REF-001",
                        "product_name": "PRODUTO TESTE 1",
                        "quantity": 5,
                        "unit_price": 100.0,
                        "total_price": 500.0
                    }
                ]
            }
        }
        
        # Primeira criação
        response1 = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        assert response1.status_code == 200
        
        # Segunda criação (duplicada)
        response2 = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        assert response2.status_code == 400
        assert "já existe" in response2.json()["detail"]
    
    def test_list_orders_success(self, client, auth_headers):
        """Testa listagem de pedidos."""
        response = client.get(
            "/api/v1/orders",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_orders_with_pagination(self, client, auth_headers):
        """Testa listagem com paginação."""
        response = client.get(
            "/api/v1/orders?page=1&per_page=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_list_orders_invalid_pagination(self, client, auth_headers):
        """Testa listagem com paginação inválida."""
        response = client.get(
            "/api/v1/orders?page=0",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Page must be >= 1" in response.json()["detail"]
    
    def test_get_order_success(self, client, auth_headers):
        """Testa busca de pedido por ID."""
        # Primeiro, criar um pedido
        order_data = {
            "pdf_data": {
                "order_number": "99999",
                "client_name": "CLIENTE BUSCA",
                "seller_name": "VENDEDOR BUSCA",
                "order_date": "2024-07-12T00:00:00",
                "total_value": 100.0,
                "items": [
                    {
                        "product_code": "999",
                        "product_reference": "REF-999",
                        "product_name": "PRODUTO BUSCA",
                        "quantity": 1,
                        "unit_price": 100.0,
                        "total_price": 100.0
                    }
                ]
            }
        }
        
        create_response = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        assert create_response.status_code == 200
        order_id = create_response.json()["id"]
        
        # Buscar o pedido
        response = client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["order_number"] == "99999"
        assert data["client_name"] == "CLIENTE BUSCA"
    
    def test_get_order_not_found(self, client, auth_headers):
        """Testa busca de pedido inexistente."""
        response = client.get(
            "/api/v1/orders/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Pedido não encontrado" in response.json()["detail"]
    
    def test_get_order_unauthenticated(self, client):
        """Testa busca sem autenticação."""
        response = client.get("/api/v1/orders/1")
        assert response.status_code == 401


class TestOrdersIntegrationFlow:
    """Testes do fluxo completo de upload e criação de pedidos."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Usuário de teste."""
        user = User(
            name="Integration User",
            pin="5678",
            role="vendedor"
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    @pytest.fixture
    async def auth_headers(self, test_user):
        """Headers de autenticação."""
        user = await test_user
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Caminho para PDF de exemplo."""
        return Path(__file__).parent.parent / "fixtures" / "pdfs" / "sample_order.pdf"
    
    def test_complete_flow_upload_preview_confirm(
        self, 
        client, 
        auth_headers, 
        sample_pdf_path,
        db_session: AsyncSession
    ):
        """Testa fluxo completo: upload -> preview -> confirmação."""
        
        # 1. Upload do PDF
        with open(sample_pdf_path, "rb") as pdf_file:
            upload_response = client.post(
                "/api/v1/orders/upload",
                headers=auth_headers,
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={
                    "logistics_type": "correios",
                    "package_type": "sacola",
                    "observations": "Fluxo completo"
                }
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert upload_data["success"] is True
        
        # 2. Confirmação do pedido
        confirm_data = {
            "pdf_data": upload_data["data"],
            "logistics_type": "correios",
            "package_type": "sacola",
            "observations": "Fluxo completo"
        }
        
        confirm_response = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=confirm_data
        )
        
        assert confirm_response.status_code == 200
        order_data = confirm_response.json()
        order_id = order_data["id"]
        
        # 3. Verificar o pedido foi criado
        get_response = client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        final_data = get_response.json()
        assert final_data["order_number"] == "12345"
        assert final_data["progress_percentage"] == 0.0
        
        # 4. Verificar na listagem
        list_response = client.get(
            "/api/v1/orders",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        orders_list = list_response.json()
        assert any(order["id"] == order_id for order in orders_list)
    
    def test_multiple_orders_different_numbers(
        self,
        client,
        auth_headers
    ):
        """Testa criação de múltiplos pedidos com números diferentes."""
        orders_data = [
            {
                "pdf_data": {
                    "order_number": f"ORD-{i:03d}",
                    "client_name": f"CLIENTE {i}",
                    "seller_name": "VENDEDOR TESTE",
                    "order_date": "2024-07-12T00:00:00",
                    "total_value": 100.0 * i,
                    "items": [
                        {
                            "product_code": f"{i:03d}",
                            "product_reference": f"REF-{i:03d}",
                            "product_name": f"PRODUTO {i}",
                            "quantity": i,
                            "unit_price": 100.0,
                            "total_price": 100.0 * i
                        }
                    ]
                }
            }
            for i in range(1, 4)
        ]
        
        created_orders = []
        for order_data in orders_data:
            response = client.post(
                "/api/v1/orders/confirm",
                headers=auth_headers,
                json=order_data
            )
            assert response.status_code == 200
            created_orders.append(response.json())
        
        # Verificar todos foram criados
        assert len(created_orders) == 3
        assert len(set(order["order_number"] for order in created_orders)) == 3
        
        # Verificar na listagem
        list_response = client.get(
            "/api/v1/orders",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        all_orders = list_response.json()
        
        created_ids = {order["id"] for order in created_orders}
        listed_ids = {order["id"] for order in all_orders}
        assert created_ids.issubset(listed_ids)


class TestOrderItemsAPI:
    """Testes para endpoints de atualização de itens."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Usuário de teste."""
        user = User(
            name="Separator User",
            pin="1111",
            role="separador"
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    @pytest.fixture
    async def auth_headers(self, test_user):
        """Headers de autenticação."""
        user = await test_user
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    async def test_order_with_items(self, client, auth_headers):
        """Cria um pedido de teste com itens."""
        order_data = {
            "pdf_data": {
                "order_number": "TEST-001",
                "client_name": "CLIENTE TESTE",
                "seller_name": "VENDEDOR TESTE",
                "order_date": "2024-07-12T00:00:00",
                "total_value": 300.0,
                "items": [
                    {
                        "product_code": "001",
                        "product_reference": "REF-001",
                        "product_name": "PRODUTO A",
                        "quantity": 2,
                        "unit_price": 50.0,
                        "total_price": 100.0
                    },
                    {
                        "product_code": "002",
                        "product_reference": "REF-002",
                        "product_name": "PRODUTO B",
                        "quantity": 1,
                        "unit_price": 200.0,
                        "total_price": 200.0
                    }
                ]
            }
        }
        
        response = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        assert response.status_code == 200
        return response.json()
    
    def test_get_order_detail(self, client, auth_headers, test_order_with_items):
        """Testa busca de detalhes do pedido com itens."""
        order_id = test_order_with_items["id"]
        
        response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == order_id
        assert data["order_number"] == "TEST-001"
        assert len(data["items"]) == 2
        
        # Verificar estrutura dos itens
        item = data["items"][0]
        assert "id" in item
        assert "product_name" in item
        assert "separated" in item
        assert "sent_to_purchase" in item
        assert item["separated"] is False
        assert item["sent_to_purchase"] is False
    
    def test_update_order_items_mark_separated(self, client, auth_headers, test_order_with_items):
        """Testa marcação de itens como separados."""
        order_id = test_order_with_items["id"]
        
        # Primeiro, buscar detalhes para pegar IDs dos itens
        detail_response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        assert detail_response.status_code == 200
        items = detail_response.json()["items"]
        
        # Marcar primeiro item como separado
        update_data = {
            "updates": [
                {
                    "item_id": items[0]["id"],
                    "separated": True
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/orders/{order_id}/items",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que item foi marcado como separado
        updated_item = next(item for item in data["items"] if item["id"] == items[0]["id"])
        assert updated_item["separated"] is True
        assert updated_item["separated_at"] is not None
        
        # Verificar que progresso foi atualizado (1 de 2 itens = 50%)
        assert data["progress_percentage"] == 50.0
    
    def test_update_order_items_send_to_purchase(self, client, auth_headers, test_order_with_items):
        """Testa envio de itens para compras."""
        order_id = test_order_with_items["id"]
        
        # Buscar detalhes para pegar IDs dos itens
        detail_response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        items = detail_response.json()["items"]
        
        # Enviar segundo item para compras
        update_data = {
            "updates": [
                {
                    "item_id": items[1]["id"],
                    "sent_to_purchase": True
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/orders/{order_id}/items",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que item foi enviado para compras
        updated_item = next(item for item in data["items"] if item["id"] == items[1]["id"])
        assert updated_item["sent_to_purchase"] is True
    
    def test_update_order_items_batch(self, client, auth_headers, test_order_with_items):
        """Testa atualização em lote de múltiplos itens."""
        order_id = test_order_with_items["id"]
        
        # Buscar detalhes para pegar IDs dos itens
        detail_response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        items = detail_response.json()["items"]
        
        # Atualizar ambos os itens
        update_data = {
            "updates": [
                {
                    "item_id": items[0]["id"],
                    "separated": True
                },
                {
                    "item_id": items[1]["id"],
                    "separated": True
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/orders/{order_id}/items",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que ambos os itens foram separados
        for item in data["items"]:
            assert item["separated"] is True
        
        # Progresso deve ser 100%
        assert data["progress_percentage"] == 100.0
    
    def test_update_order_items_invalid_item(self, client, auth_headers, test_order_with_items):
        """Testa atualização com ID de item inválido."""
        order_id = test_order_with_items["id"]
        
        update_data = {
            "updates": [
                {
                    "item_id": 99999,  # ID inexistente
                    "separated": True
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/orders/{order_id}/items",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 400
        assert "não encontrado" in response.json()["detail"]
    
    def test_send_specific_item_to_purchase(self, client, auth_headers, test_order_with_items):
        """Testa endpoint específico para enviar item para compras."""
        order_id = test_order_with_items["id"]
        
        # Buscar detalhes para pegar ID do item
        detail_response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        items = detail_response.json()["items"]
        item_id = items[0]["id"]
        
        response = client.patch(
            f"/api/v1/orders/{order_id}/items/{item_id}/purchase",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["item_id"] == item_id
        assert "purchase_item_id" in data
    
    def test_send_item_to_purchase_already_sent(self, client, auth_headers, test_order_with_items):
        """Testa envio de item já enviado para compras."""
        order_id = test_order_with_items["id"]
        
        # Buscar detalhes e enviar item
        detail_response = client.get(
            f"/api/v1/orders/{order_id}/detail",
            headers=auth_headers
        )
        items = detail_response.json()["items"]
        item_id = items[0]["id"]
        
        # Primeiro envio
        response1 = client.patch(
            f"/api/v1/orders/{order_id}/items/{item_id}/purchase",
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # Segundo envio (deve falhar)
        response2 = client.patch(
            f"/api/v1/orders/{order_id}/items/{item_id}/purchase",
            headers=auth_headers
        )
        assert response2.status_code == 400
        assert "já foi enviado" in response2.json()["detail"]
    
    def test_update_items_nonexistent_order(self, client, auth_headers):
        """Testa atualização de itens em pedido inexistente."""
        update_data = {
            "updates": [
                {
                    "item_id": 1,
                    "separated": True
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/orders/99999/items",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 404
        assert "Pedido não encontrado" in response.json()["detail"]
    
    def test_get_order_detail_nonexistent(self, client, auth_headers):
        """Testa busca de detalhes de pedido inexistente."""
        response = client.get(
            f"/api/v1/orders/99999/detail",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Pedido não encontrado" in response.json()["detail"]


class TestOrderStatsAPI:
    """Testes para endpoint de estatísticas."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Usuário de teste."""
        user = User(
            name="Admin User",
            pin="0000",
            role="admin"
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    @pytest.fixture
    async def auth_headers(self, test_user):
        """Headers de autenticação."""
        user = await test_user
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_orders_stats_empty(self, client, auth_headers):
        """Testa estatísticas com banco vazio."""
        response = client.get(
            "/api/v1/orders/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura das estatísticas
        expected_fields = [
            "total_orders", "orders_in_progress", "orders_completed", 
            "orders_pending", "total_items", "items_separated", 
            "items_in_purchase", "average_separation_time"
        ]
        
        for field in expected_fields:
            assert field in data
        
        # Com banco vazio, valores devem ser 0 ou None
        assert data["total_orders"] == 0
        assert data["orders_pending"] == 0
        assert data["total_items"] == 0
    
    def test_get_orders_stats_with_data(self, client, auth_headers):
        """Testa estatísticas com dados."""
        # Primeiro criar um pedido
        order_data = {
            "pdf_data": {
                "order_number": "STATS-001",
                "client_name": "CLIENTE STATS",
                "seller_name": "VENDEDOR STATS",
                "order_date": "2024-07-12T00:00:00",
                "total_value": 100.0,
                "items": [
                    {
                        "product_code": "001",
                        "product_reference": "REF-001",
                        "product_name": "PRODUTO STATS",
                        "quantity": 1,
                        "unit_price": 100.0,
                        "total_price": 100.0
                    }
                ]
            }
        }
        
        create_response = client.post(
            "/api/v1/orders/confirm",
            headers=auth_headers,
            json=order_data
        )
        assert create_response.status_code == 200
        
        # Buscar estatísticas
        response = client.get(
            "/api/v1/orders/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter pelo menos 1 pedido
        assert data["total_orders"] >= 1
        assert data["total_items"] >= 1
    
    def test_get_orders_stats_unauthenticated(self, client):
        """Testa acesso às estatísticas sem autenticação."""
        response = client.get("/api/v1/orders/stats")
        assert response.status_code == 401