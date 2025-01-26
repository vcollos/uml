import gradio as gr
import base64
from google.auth import default
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

# Usa as credenciais padrão configuradas com `gcloud auth`
credentials, project = default()

# Inicializa o cliente AI Platform com as credenciais padrão
aiplatform.init(credentials=credentials, project=project)

def predict_image_classification_sample(
    filename: str,
    project: str = "366594249966",
    endpoint_id: str = "2478766501448908800",
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # Configuração do cliente
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Lê e codifica a imagem
    with open(filename, "rb") as f:
        file_content = f.read()

    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content
    ).to_value()
    instances = [instance]

    # Configurar parâmetros da predição
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5, max_predictions=5
    ).to_value()

    # Montar o endpoint
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)

    # Realizar a predição
    response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)

    if not hasattr(response, "predictions"):
        raise ValueError("Nenhuma predição encontrada no endpoint.")

    # Processar os resultados
    predictions = response.predictions
    results = []
    for prediction in predictions:
        pred_dict = dict(prediction)
        results.append(pred_dict)

    return results

def classify_image(image):
    temp_path = "/tmp/uploaded_image.jpg"
    image.save(temp_path)

    try:
        # Fazer a predição
        results = predict_image_classification_sample(filename=temp_path)
        if not results:
            return "Nenhuma predição encontrada."

        predictions = [
            f"{res.get('displayNames', [''])[0]}: {res.get('confidences', [0])[0] * 100:.2f}%"
            for res in results
        ]

        if predictions:
            return "## Resultado\n" + "\n".join(f"## {p}" for p in predictions)
        return "## Nenhuma predição válida encontrada."
    except Exception as e:
        return f"Erro ao processar a imagem: {str(e)}"

# Interface Gradio
with gr.Blocks() as interface:
    gr.Image(value="logo.png", label="", interactive=False, width=300, elem_id="logo", show_label=False)
    gr.Markdown("### Auditor Digital")

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

    submit_btn.click(fn=classify_image, inputs=image_input, outputs=result_output)
    clear_btn.click(lambda: [None, ""], outputs=[image_input, result_output])

interface.launch()