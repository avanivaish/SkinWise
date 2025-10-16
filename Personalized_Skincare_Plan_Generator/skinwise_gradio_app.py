import gradio as gr
import pandas as pd
from personalized_skincare_plan import load_product_data, generate_skincare_plan

skin_types = ['Oily', 'Dry', 'Normal', 'Sensitive', 'None']
concern_types = ['Acne', 'Spots', 'Pigmentation', 'Tan', 'Hydration', 'Blemish', 'Aging', 'Pores', 'None']
routines = ['Morning', 'Night', 'Both']

def skincare_ui(skin_type, concern, routine):
    df = load_product_data()
    result = generate_skincare_plan(df, skin_type, concern, routine)
    return result

with gr.Blocks() as demo:
    gr.Markdown(
        "<h1 style='color:#F4BFBF;'>SkinWise: Personalized Skincare Routines</h1>"
        "Select your skin type and main concern to get a customized AM/PM skincare product recommendation.<br/>"
        "Based on Plum Goodness product data."
    )

    with gr.Row():
        skin_type_in = gr.Dropdown(skin_types, label="Skin Type")
        concern_in = gr.Dropdown(concern_types, label="Main Concern")
        routine_in = gr.Dropdown(routines, label="Routine")

    get_btn = gr.Button("✨ Get My Routine ✨", elem_id="run-btn", scale=2)
    output_md = gr.Markdown(label="Personalized Skincare Plan")

    get_btn.click(fn=skincare_ui, inputs=[skin_type_in, concern_in, routine_in], outputs=output_md)

if __name__ == "__main__":
    demo.launch(share=False)
