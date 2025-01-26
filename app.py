import gradio as gr
import base64
import os
from google.auth import default
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

# Obtém credenciais e projeto do ambiente configurado no Google Cloud CLI
credentials, project = default()

# Inicializar o cliente AI Platform
aiplatform.init(credentials=credentials, project=project)

def predict_image_classification_sample(
    endpoint_id: str = "2478766501448908800",
    filename: str = "YOUR_IMAGE_FILE",
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # Configuração do cliente
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Ler e codificar a imagem
    with open(filename, "rb") as f:
        file_content = f.read()

    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content
    ).to_value()
    instances = [instance]

    # Configurar os parâmetros da predição
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5,
        max_predictions=5,
    ).to_value()

    # Obter o endpoint completo
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)

    # Realizar a predição
    response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)

    if not hasattr(response, "predictions"):
        raise ValueError("Resposta inválida do endpoint: nenhuma predição encontrada")

    # Processar os resultados
    predictions = response.predictions
    results = []
    for prediction in predictions:
        pred_dict = dict(prediction)
        print(" prediction:", pred_dict)
        results.append(pred_dict)

    return results


def classify_image(image):
    # Salva a imagem temporariamente
    temp_path = "/tmp/uploaded_image.jpg"
    image.save(temp_path)
    
    try:
        # Chamar a predição
        results = predict_image_classification_sample(filename=temp_path)
        if not results:
            return "Nenhuma predição encontrada"
        
        predictions = []
        for result in results:
            if isinstance(result, dict):
                if 'displayNames' in result and 'confidences' in result:
                    for name, confidence in zip(result['displayNames'], result['confidences']):
                        predictions.append(f"{name}: {confidence*100:.2f}%")
        
        if predictions:
            return "## Resultado\n" + "\n".join(f"## {p}" for p in predictions)
        return f"## Nenhuma predição válida encontrada\nResultado bruto: {str(results)}"
    except Exception as e:
        return f"Erro ao processar a imagem: {str(e)}"


# Interface Gradio
with gr.Blocks() as interface:
    # Layout
    gr.Image(value="logo.png", label="", interactive=False, width=300, elem_id="logo", show_label=False)
    gr.Markdown("### Auditor Digital")

    # Upload e Resultados
    with gr.Row():
        with gr.Column():
            clear_btn = gr.Button("Limpar")
    with gr.Row():
        with gr.Column():
            submit_btn = gr.Button("Auditar")
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Enviar Imagem")
    with gr.Row():
        with gr.Column():
            result_output = gr.Markdown(label="## Resultado")

    # Conexões dos Botões
    submit_btn.click(fn=classify_image, inputs=image_input, outputs=result_output)
    clear_btn.click(lambda: [None, ""], outputs=[image_input, result_output])

# Iniciar a Interface
interface.launch()