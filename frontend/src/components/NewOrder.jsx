import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../components/ToastContainer';
import Sidebar from './Sidebar';
import { debugLog, incrementCounter } from '../utils/debug';
import { api } from '../services/api';

function NewOrder() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [step, setStep] = useState(1); // 1: Upload, 2: Preview, 3: Confirm
  const [formData, setFormData] = useState({
    logistics: '',
    packageType: '',
    observations: ''
  });
  const [uploadedFile, setUploadedFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);

  debugLog('newOrder', 'RENDER', {
    step,
    hasFile: !!uploadedFile,
    hasExtractedData: !!extractedData,
    renderCount: incrementCounter('newOrderRender')
  });

  const logisticsOptions = [
    'Lalamove',
    'Correios', 
    'Melhor Envio',
    'Retirada',
    'Entrega',
    'Cliente na loja',
    'Ônibus'
  ];

  const packageTypes = ['Caixa', 'Sacola'];

  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileUpload = async (file) => {
    if (!file || file.type !== 'application/pdf') {
      addToast('Por favor, selecione um arquivo PDF válido', 'error');
      return;
    }

    setLoading(true);
    setUploadedFile(file);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload PDF and extract data
      const response = await api.post('/orders/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // The API returns a PDFPreviewResponse with success, message, data, errors
      if (response.data.success && response.data.data) {
        setExtractedData(response.data.data);
        addToast(response.data.message || 'PDF processado com sucesso!', 'success');
      } else {
        throw new Error(response.data.message || 'Erro ao processar PDF');
      }
      
      debugLog('newOrder', 'PDF_UPLOADED', {
        fileName: file.name,
        extractedData: response.data
      });
      
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setUploadedFile(null);
      setExtractedData(null);
      
      // Handle backend validation errors
      let errorMessage = 'Erro ao processar PDF';
      
      if (error.response?.data) {
        const data = error.response.data;
        if (data.message) {
          errorMessage = data.message;
        } else if (data.errors && Array.isArray(data.errors)) {
          errorMessage = data.errors.join(', ');
        } else if (data.detail) {
          errorMessage = data.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      addToast(errorMessage, 'error');
      
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const canProceedToPreview = () => {
    return extractedData && formData.logistics && formData.packageType;
  };

  const handleCreateOrder = async () => {
    if (!extractedData) {
      addToast('Dados do pedido não encontrados', 'error');
      return;
    }

    setLoading(true);
    
    try {
      // Prepare the order data for creation
      const orderData = {
        pdf_data: extractedData,
        logistics_type: formData.logistics,
        package_type: formData.packageType,
        observations: formData.observations || '',
      };
      
      // Create the order using the /confirm endpoint
      const response = await api.post('/orders/confirm', orderData);
      
      debugLog('newOrder', 'ORDER_CREATED', {
        orderId: response.data.id,
        orderNumber: response.data.order_number
      });
      
      addToast('Pedido criado com sucesso!', 'success');
      
      // Navigate back to dashboard
      navigate('/');
      
    } catch (error) {
      console.error('Error creating order:', error);
      
      let errorMessage = 'Erro ao criar pedido';
      
      if (error.response?.data?.detail) {
        // Handle both string and array/object error formats
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          // Pydantic validation errors come as array
          errorMessage = detail.map(err => err.msg || err.message || 'Erro de validação').join(', ');
        } else if (typeof detail === 'object' && detail.msg) {
          errorMessage = detail.msg;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      addToast(errorMessage, 'error');
      
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              📦 Novo Pedido
            </h1>
            <p className="text-gray-600">
              Faça upload do PDF do pedido e configure as informações de entrega
            </p>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div className={`flex items-center ${step >= 1 ? 'text-orange-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 
                  ${step >= 1 ? 'border-orange-600 bg-orange-600 text-white' : 'border-gray-300'}`}>
                  1
                </div>
                <span className="ml-2 font-medium">Upload</span>
              </div>
              <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-orange-600' : 'bg-gray-300'}`}></div>
              <div className={`flex items-center ${step >= 2 ? 'text-orange-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 
                  ${step >= 2 ? 'border-orange-600 bg-orange-600 text-white' : 'border-gray-300'}`}>
                  2
                </div>
                <span className="ml-2 font-medium">Preview</span>
              </div>
              <div className={`flex-1 h-1 mx-4 ${step >= 3 ? 'bg-orange-600' : 'bg-gray-300'}`}></div>
              <div className={`flex items-center ${step >= 3 ? 'text-orange-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 
                  ${step >= 3 ? 'border-orange-600 bg-orange-600 text-white' : 'border-gray-300'}`}>
                  3
                </div>
                <span className="ml-2 font-medium">Confirmar</span>
              </div>
            </div>
          </div>

          {/* Step 1: Upload and Configuration */}
          {step === 1 && (
            <div className="space-y-6">
              {/* File Upload */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  📄 Upload do PDF
                </h2>
                
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
                    ${loading 
                      ? 'border-orange-400 bg-orange-50' 
                      : uploadedFile 
                        ? 'border-green-400 bg-green-50' 
                        : 'border-gray-300 hover:border-orange-400'
                    }`}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  <div className="mb-4">
                    {loading ? (
                      <svg className="animate-spin mx-auto h-12 w-12 text-orange-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : uploadedFile && extractedData ? (
                      <svg className="mx-auto h-12 w-12 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                  
                  <div className="text-lg font-medium text-gray-900 mb-2">
                    {loading ? (
                      <span className="text-orange-600">Processando PDF...</span>
                    ) : uploadedFile && extractedData ? (
                      <span className="text-green-600">✓ {uploadedFile.name} - Processado com sucesso!</span>
                    ) : uploadedFile ? (
                      <span className="text-yellow-600">📄 {uploadedFile.name} - Processando...</span>
                    ) : (
                      'Arraste o PDF aqui ou clique para selecionar'
                    )}
                  </div>
                  
                  <p className="text-gray-500 mb-4">
                    {loading 
                      ? 'Extraindo dados do PDF, aguarde...' 
                      : uploadedFile && extractedData 
                        ? `${extractedData.items?.length || 0} itens extraídos com sucesso`
                        : 'Apenas arquivos PDF são aceitos'
                    }
                  </p>
                  
                  {!loading && (
                    <>
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileInputChange}
                        className="hidden"
                        id="file-upload"
                        disabled={loading}
                      />
                      <label
                        htmlFor="file-upload"
                        className={`inline-flex items-center px-4 py-2 rounded-lg cursor-pointer transition-colors
                          ${uploadedFile && extractedData
                            ? 'bg-green-600 text-white hover:bg-green-700'
                            : 'bg-orange-600 text-white hover:bg-orange-700'
                          }`}
                      >
                        {uploadedFile && extractedData ? 'Trocar Arquivo' : 'Selecionar Arquivo'}
                      </label>
                    </>
                  )}
                </div>
              </div>

              {/* Logistics Selection */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  🚚 Tipo de Logística
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {logisticsOptions.map((option) => (
                    <button
                      key={option}
                      onClick={() => handleFormChange('logistics', option)}
                      className={`p-3 rounded-lg border text-sm font-medium transition-all
                        ${formData.logistics === option
                          ? 'border-orange-600 bg-orange-50 text-orange-700'
                          : 'border-gray-300 hover:border-gray-400'
                        }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>

              {/* Package Type */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  📦 Tipo de Embalagem
                </h2>
                
                <div className="flex gap-3">
                  {packageTypes.map((type) => (
                    <button
                      key={type}
                      onClick={() => handleFormChange('packageType', type)}
                      className={`flex-1 p-4 rounded-lg border font-medium transition-all
                        ${formData.packageType === type
                          ? 'border-orange-600 bg-orange-50 text-orange-700'
                          : 'border-gray-300 hover:border-gray-400'
                        }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Observations */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  📝 Observações
                </h2>
                
                <textarea
                  value={formData.observations}
                  onChange={(e) => handleFormChange('observations', e.target.value)}
                  placeholder="Observações adicionais para o pedido..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                  rows={4}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between">
                <button
                  onClick={() => navigate('/')}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                
                <button
                  onClick={() => setStep(2)}
                  disabled={!canProceedToPreview()}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors
                    ${canProceedToPreview()
                      ? 'bg-orange-600 text-white hover:bg-orange-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                >
                  Próximo: Preview
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Preview */}
          {step === 2 && extractedData && (
            <div className="space-y-6">
              {/* Order Summary */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  👀 Preview do Pedido
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Número do Orçamento
                    </label>
                    <input
                      type="text"
                      value={extractedData.order_number || ''}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cliente
                    </label>
                    <input
                      type="text"
                      value={extractedData.client_name || ''}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Vendedor
                    </label>
                    <input
                      type="text"
                      value={extractedData.seller_name || ''}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Data
                    </label>
                    <input
                      type="text"
                      value={extractedData.order_date ? new Date(extractedData.order_date).toLocaleDateString('pt-BR') : ''}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Valor Total
                    </label>
                    <input
                      type="text"
                      value={extractedData.total_value ? `R$ ${extractedData.total_value}` : ''}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Total de Itens
                    </label>
                    <input
                      type="text"
                      value={extractedData.items ? extractedData.items.length : '0'}
                      readOnly
                      className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                </div>
                
                {/* Configuration Summary */}
                <div className="border-t pt-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Configurações</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Logística
                      </label>
                      <input
                        type="text"
                        value={formData.logistics}
                        readOnly
                        className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Embalagem
                      </label>
                      <input
                        type="text"
                        value={formData.packageType}
                        readOnly
                        className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Observações
                      </label>
                      <input
                        type="text"
                        value={formData.observations || 'Nenhuma observação'}
                        readOnly
                        className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Items List */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  📦 Itens do Pedido ({extractedData.items ? extractedData.items.length : 0})
                </h3>
                
                {extractedData.items && extractedData.items.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2 font-medium text-gray-700">Código</th>
                          <th className="text-left p-2 font-medium text-gray-700">Nome</th>
                          <th className="text-left p-2 font-medium text-gray-700">Quantidade</th>
                          <th className="text-left p-2 font-medium text-gray-700">Valor Unit.</th>
                          <th className="text-left p-2 font-medium text-gray-700">Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {extractedData.items.map((item, index) => (
                          <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="p-2 text-sm">{item.product_code || ''}</td>
                            <td className="p-2 text-sm">{item.product_name || ''}</td>
                            <td className="p-2 text-sm">{item.quantity || ''}</td>
                            <td className="p-2 text-sm">{item.unit_price ? `R$ ${item.unit_price.toFixed(2)}` : ''}</td>
                            <td className="p-2 text-sm">{item.total_price ? `R$ ${item.total_price.toFixed(2)}` : ''}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    Nenhum item encontrado no PDF
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Voltar
                </button>
                
                <button
                  onClick={() => setStep(3)}
                  className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Próximo: Confirmar
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Confirmation */}
          {step === 3 && extractedData && (
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                ✅ Confirmação do Pedido
              </h2>
              
              {/* Final Summary */}
              <div className="mb-6 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <h3 className="font-semibold text-orange-800 mb-2">
                  Resumo Final
                </h3>
                <div className="text-sm text-orange-700 space-y-1">
                  <p><strong>Orçamento:</strong> #{extractedData.order_number}</p>
                  <p><strong>Cliente:</strong> {extractedData.client_name}</p>
                  <p><strong>Vendedor:</strong> {extractedData.seller_name}</p>
                  <p><strong>Itens:</strong> {extractedData.items ? extractedData.items.length : 0} produtos</p>
                  <p><strong>Valor Total:</strong> R$ {extractedData.total_value}</p>
                  <p><strong>Logística:</strong> {formData.logistics}</p>
                  <p><strong>Embalagem:</strong> {formData.packageType}</p>
                  {formData.observations && (
                    <p><strong>Observações:</strong> {formData.observations}</p>
                  )}
                </div>
              </div>
              
              {/* Warning/Info */}
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="text-sm text-blue-700">
                    <p className="font-medium mb-1">Antes de confirmar:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Verifique se todos os dados estão corretos</li>
                      <li>Confirme se todos os itens foram extraídos do PDF</li>
                      <li>Após a criação, o pedido estará disponível para separação</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex justify-between">
                <button
                  onClick={() => setStep(2)}
                  disabled={loading}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Voltar
                </button>
                
                <button
                  onClick={handleCreateOrder}
                  disabled={loading}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center
                    ${loading 
                      ? 'bg-gray-400 text-gray-200 cursor-not-allowed' 
                      : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Criando Pedido...
                    </>
                  ) : (
                    '✅ Criar Pedido'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default NewOrder;