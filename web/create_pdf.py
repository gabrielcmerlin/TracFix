from bs4 import BeautifulSoup
from weasyprint import HTML

def update_section_content(html_file, section_id, new_content):
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the section by ID
    section = soup.find(id=section_id)
    if section:
        # Update the content of the section
        section.string = new_content
        print(f"Content of section with ID '{section_id}' updated.")

        # Save the modified HTML back to the file
        with open(html_file, 'w', encoding='utf-8') as file:
            file.write(str(soup))
    else:
        print(f"Section with ID '{section_id}' not found.")

html_file = './web/page.html'
ids = [
    "num_ordem_servico",
    "data_vencimento",
    "titulo",
    "responsaveis",
    "status",
    "categoria",
    "tags",
    "data_criacao",
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

if __name__ == '__main__':

    # ordens_servico = 
    # for i, ordem in enumerate(ordens_servico):
    #     infos_ordem = {}
    #     for current_id in ids:
    #         infos_ordem[current_id] = 'Undefined'

    #     for key in infos_ordem:
    #         update_section_content(html_file, key, infos_ordem[key])

    #     pdf_file = './pdf_results/output' + str(i) + '.pdf'
    #     HTML(html_file).write_pdf(pdf_file)