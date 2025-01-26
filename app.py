import gradio as gr
import base64
import os
from google.cloud.aiplatform.gapic.schema import predict
import json
import os
from google.auth import default
from google.cloud import aiplatform

# Obtém credenciais do ambiente padrão
credentials, project = default()

# Configurar o cliente com as credenciais obtidas
aiplatform.init(credentials=credentials, project=project)


def predict_image_classification_sample(
    project: str = "366594249966",
    endpoint_id: str = "2478766501448908800",
    filename: str = "YOUR_IMAGE_FILE",
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):

    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    from google.oauth2 import service_account
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    client = aiplatform.gapic.PredictionServiceClient(
        client_options=client_options,
        credentials=credentials
    )
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5,
        max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    if not hasattr(response, 'predictions'):
        raise ValueError("Resposta inválida do endpoint: nenhuma predição encontrada")
    
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
    
    # Chama a função de predição
    try:
        results = predict_image_classification_sample(filename=temp_path)
        if not results:
            return "Nenhuma predição encontrada"
            
        predictions = []
        for result in results:
            if isinstance(result, dict):
                if 'displayNames' in result and 'confidences' in result:
                    for name, confidence in zip(result['displayNames'], result['confidences']):
                        predictions.append(f"{name}: {confidence*100:.2f}%")
                elif 'confidences' in result and 'displayNames' in result:
                    for name, confidence in zip(result['displayNames'], result['confidences']):
                        predictions.append(f"{name}: {confidence*100:.2f}%")
        
        if predictions:
            return "## Resultado\n" + "\n".join(f"## {p}" for p in predictions)
        return f"## Nenhuma predição válida encontrada\nResultado bruto: {str(results)}"
    except Exception as e:
        return f"Erro ao processar a imagem: {str(e)}"


# Layout customizado
with gr.Blocks() as interface:
    # Logo no topo
    gr.Image(value="logo.png", label="", interactive=False, width=300, elem_id="logo", show_label=False)
    
    # Título
    gr.Markdown("### Auditor Digital")

    # Área de upload e resultado
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
    # Conexões
    submit_btn.click(fn=classify_image, inputs=image_input, outputs=result_output)
    clear_btn.click(lambda: [None, ""], outputs=[image_input, result_output])

# Inicia a interface
interface.launch()