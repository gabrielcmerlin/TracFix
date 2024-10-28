from bs4 import BeautifulSoup
import pdfkit
import rag
import json

def update_section_content(html_file, section_id, new_content):
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the section by ID
    section = soup.find(id=section_id)
    if section:
        # Update the content of the section
        section.string = new_content

        # Save the modified HTML back to the file
        with open(html_file, 'w', encoding='utf-8') as file:
            file.write(str(soup))
    else:
        print(f"Section with ID '{section_id}' not found.")

html_file = './chatgpt/page.html'
ids = [
    "num_ordem_servico",
    "data_vencimento",
    "titulo",
    "responsaveis",
    "status",
    "categoria",
    "tags",
    "data_criado",
    "nome_ativo",
    "modelo",
    "tags_ativo",
    "titulo_atividades",
    "tipo_atividades",
    "status_atividades",
    "horas_atividades",
    "executante_atividades",
    "passo_a_passo",
    "ferramentas"
]

options = {
    'no-stop-slow-scripts': None,
    'disable-smart-shrinking': None,
    'ignore-load-errors': None,
}

def create_html_pdfs():
    pdf_names = []

    json_string = ((rag.get_question()).replace('json','')).replace('`', '')
    ordens_servico = json.loads(json_string)

    for ordem in ordens_servico:

        infos_ordem = {}
        for current_id in ids:
            infos_ordem[current_id] = 'Undefined'

        infos_ordem['passo_a_passo'] = ordem['passo_a_passo']
        infos_ordem['ferramentas'] = ordem['ferramentas']

        for key in infos_ordem:
            update_section_content(html_file, key, infos_ordem[key])

        pdf_file = './pdf_results/' + ordem['titulo'] + '.pdf'

        try:
            pdfkit.from_file(html_file, pdf_file)
        except:
            print('Feito o ', pdf_file)

        pdf_names.append(pdf_file)

    return pdf_names

print(create_html_pdfs())