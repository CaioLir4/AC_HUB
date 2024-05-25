import os
import tkinter as tk
from functools import partial
import subprocess
from tkinter import simpledialog, messagebox
from datetime import datetime

versoes = {
    "3.1.6_5": {"22-01-2024", "21-01-2024"},
    "3.1.6_4": {"11-01-2024"},
    "3.1.5": {"30-11-2023", "31-11-2023", "07-07-2023"},
    "3.1.4": {"26-04-2022"},
}
config_mostrada = False

def encontrar_diretorios_lc_sistemas():
    diretorios_lc_sistemas = []
    disco_c = 'C:\\'
    for nome in os.listdir(disco_c):
        if nome.startswith("LC sistemas - Softhouse") and os.path.isdir(os.path.join(disco_c, nome)):
            diretorios_lc_sistemas.append(os.path.join(disco_c, nome))
    return diretorios_lc_sistemas

def abrir_diretorio(diretorio):
    os.startfile(diretorio)

def criar_botoes_abrir_diretorios(root):
    diretorios_lc_sistemas = encontrar_diretorios_lc_sistemas()
    for diretorio in diretorios_lc_sistemas:
        nome_pasta = os.path.basename(diretorio)
        btn = tk.Button(root, text=nome_pasta, command=lambda dir=diretorio: abrir_diretorio(dir), font=("Helvetica", 12), bg="#2196F3", fg="white", bd=0, padx=10, pady=5, width=20)
        btn.pack(pady=5)

def get_file_modification_date(file_path):
    command = f'powershell -command "(Get-Item \'{file_path}\').LastWriteTime.ToString(\'dd-MM-yyyy\')"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

def verificar_senha():
    senha_correta = "40028922"
    senha = simpledialog.askstring("Senha", "Digite a senha:", show='*')
    if senha == senha_correta:
        return True
    else:
        messagebox.showerror("Erro", "Senha incorreta!")
        return False

def extrair_ip_do_arquivo_rede(caminho_arquivo):
    ip = None
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if linha.startswith("IP:"):
                    ip = linha.split(":")[1].strip()
                    break
    except FileNotFoundError:
        return "Arquivo 'rede.txt' não encontrado."
    return ip

def extrair_versao_do_arquivo_rede(caminho_arquivo):
    versao_REMOTA = None
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if linha.startswith("VERSAO:"):
                    versao_REMOTA = linha.split(":")[1].strip()
                    break
    except FileNotFoundError:
        return "Arquivo 'rede.txt' não encontrado."
    return versao_REMOTA

def alterar_ip_no_arquivo_rede(caminho_arquivo, novo_ip):
    linhas = []
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    with open(caminho_arquivo, 'w') as arquivo:
        for linha in linhas:
            if linha.startswith("IP:"):
                arquivo.write(f"IP:{novo_ip}\n")
            else:
                arquivo.write(linha)

def alterar_versao_no_arquivo_rede(caminho_arquivo, novo_versao):
    linhas = []
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    with open(caminho_arquivo, 'w') as arquivo:
        versao_existe = False
        for linha in linhas:
            if linha.startswith("VERSAO:") or linha.startswith("VERSAO: "):
                arquivo.write(f"VERSAO:{novo_versao}\n")
                versao_existe = True
            else:
                arquivo.write(linha)

        if not versao_existe:
            arquivo.write(f"\nVERSAO:{novo_versao}")

def obter_data_modificacao_jar(caminho_jar):
    timestamp = os.path.getmtime(caminho_jar)
    data_modificacao = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
    return data_modificacao

def obter_versao_correspondente(data_modificacao):
    for versao, datas in versoes.items():
        if data_modificacao in datas:
            return versao
    return "Versão não encontrada"

def executar_programa_java(caminho_pasta, log_text):
    caminho_java = os.path.join(caminho_pasta, "jre", "bin", "javaw.exe")
    argumento_jar = '-jar'
    argumento_memoria = '-Xms1024m'
    caminho_jar = os.path.join(caminho_pasta, 'PI.jar')
    cwd = caminho_pasta
    comando = [caminho_java, argumento_jar, argumento_memoria, caminho_jar]

    caminho_arquivo_rede = os.path.join(caminho_pasta, "rede.txt")

    if os.path.exists(caminho_arquivo_rede):
        ip = extrair_ip_do_arquivo_rede(caminho_arquivo_rede)
        if ip:
            log_text.insert(tk.END, f"IP encontrado: {ip}\n")
            comando.extend(['-Dip=' + ip])

    if os.path.exists(caminho_jar):
        data_modificacao = obter_data_modificacao_jar(caminho_jar)
        versao = obter_versao_correspondente(data_modificacao)
        log_text.insert(tk.END, f"Data do PI.jar: {data_modificacao} - Versão Local: {versao}\n")
    else:
        versao = "Arquivo PI.jar não encontrado."
        log_text.insert(tk.END, f"Versão Local: {versao}\n")
    try:
        versao_REMOTA = extrair_versao_do_arquivo_rede(caminho_arquivo_rede)
        print(versao_REMOTA)
        if versao == versao_REMOTA:
            subprocess.Popen(comando, cwd=cwd)
        else:
            messagebox.showerror("Erro", "Versões incompatíveis! Acesso Bloqueado!")

    except FileNotFoundError:
        messagebox.showerror("Erro", "{}'")


    return versao

def remover_prefixos(texto, prefixos):
    for prefixo in prefixos:
        if texto.startswith(prefixo):
            return texto[len(prefixo):].strip()
    return texto.strip()

def alterar_ip(caminho_arquivo_rede, ip_entry):
    novo_ip = ip_entry.get()
    if os.path.exists(caminho_arquivo_rede):
        alterar_ip_no_arquivo_rede(caminho_arquivo_rede, novo_ip)
        log_text.insert(tk.END, f"{caminho_arquivo_rede}, IP alterado para: {novo_ip}\n")
    else:
        log_text.insert(tk.END, f"Erro: arquivo {caminho_arquivo_rede} não encontrado.\n")
def alterar_versao(caminho_arquivo_rede, vr_entry):
    novo_versao = vr_entry.get()
    if os.path.exists(caminho_arquivo_rede):
        alterar_versao_no_arquivo_rede(caminho_arquivo_rede, novo_versao)
        log_text.insert(tk.END, f"{caminho_arquivo_rede}, Versão alterada para: {novo_versao}\n")
    else:
        log_text.insert(tk.END, f"Erro: arquivo {caminho_arquivo_rede} não encontrado.\n")

def on_clicar_botao(pasta, nome_pasta, log_text):
    log_text.insert(tk.END, f"Botão clicado para a pasta {nome_pasta}\n")
    executar_programa_java(pasta, log_text)

def mudar_tamanho(novo_largura, novo_altura):
    root.geometry(f"{novo_largura}x{novo_altura}")


def criar_botoes_atualizado(root):
    pastas = [f.path for f in os.scandir("C:/") if f.is_dir() and "LC sistemas - Softhouse" in f.name]
    config_frames = []
    rede_inexistente = []

    def config_button_action():
        global config_mostrada
        if verificar_senha():
            mostrar_ou_esconder_todas_configuracoes(config_frames, log_frame)
            if config_mostrada:
                mudar_tamanho(400, 400)
            else:
                mudar_tamanho(1500, 650)
            config_mostrada = not config_mostrada

    for pasta in pastas:
        nome_pasta_completo = os.path.basename(pasta)
        nome_pasta = remover_prefixos(nome_pasta_completo, ["LC sistemas - Softhouse_", "LC sistemas - Softhouse"])

        frame = tk.Frame(root, bg="#f0f0f0", bd=2, relief=tk.GROOVE)
        frame.pack(pady=5, fill='x')

        caminho_jar = os.path.join(pasta, 'PI.jar')
        versao = "Versão não encontrada"

        btn_bg_color = "#F44336"

        caminho_arquivo_rede = os.path.join(pasta, "rede.txt")
        ip = None
        versao_REMOTA = None

        if os.path.exists(caminho_arquivo_rede):
            ip = extrair_ip_do_arquivo_rede(caminho_arquivo_rede)
            versao_REMOTA = extrair_versao_do_arquivo_rede(caminho_arquivo_rede)
            if ip:
                log_text.insert(tk.END, f"Arquivo 'rede.txt' encontrado em {nome_pasta}. IP: {ip}\n")
            else:
                log_text.insert(tk.END, f"Arquivo 'rede.txt' encontrado em {nome_pasta}, mas IP não encontrado.\n")
        else:
            log_text.insert(tk.END, f"Arquivo 'rede.txt' não encontrado em {nome_pasta}\n")
            rede_inexistente.append(nome_pasta)

        if os.path.exists(caminho_jar):
            data_modificacao = obter_data_modificacao_jar(caminho_jar)
            versao = obter_versao_correspondente(data_modificacao)

            if versao == versao_REMOTA:
                btn_bg_color = "#4CAF50"

        # Criar botão para cada pasta
        btn = tk.Button(frame, text=nome_pasta, command=partial(on_clicar_botao, pasta, nome_pasta_completo, log_text),
                        font=("Helvetica", 12), bg=btn_bg_color, fg="white", bd=0, padx=10, pady=5, width=20)
        btn.pack(side='left', padx=5, pady=5)

        config_frame = tk.Frame(frame, bg="#ffffff")

        # Criar botão para abrir o diretório correspondente
        btn_abrir_diretorio = tk.Button(config_frame, text="Abrir Diretório", command=lambda path=pasta: abrir_diretorio(path),
                                        font=("Helvetica", 12), bg="#2196F3", fg="white", bd=0, padx=10, pady=5,
                                        width=20)
        btn_abrir_diretorio.pack(side='left', padx=5, pady=5)

        label_versao = tk.Label(frame, text=f"Versão local: {versao}", font=("Helvetica", 12), bg="#f0f0f0", bd=0,
                                padx=10, pady=5, width=20)
        label_versao.pack(side='left', padx=5, pady=5)

        ip_label = tk.Label(config_frame, text="IP:", font=("Helvetica", 12), bg="#ffffff")
        ip_label.pack(side='left', padx=5, pady=5)

        ip_entry = tk.Entry(config_frame, font=("Helvetica", 12), bd=1, relief=tk.SOLID)
        ip_entry.pack(side='left', padx=5, pady=5)
        ip_entry.insert(0, ip if ip else '')

        salvar_btn = tk.Button(config_frame, text="Salvar IP",
                               command=partial(alterar_ip, caminho_arquivo_rede, ip_entry),
                               font=("Helvetica", 12), bg="#2196F3", fg="white", bd=0, padx=10, pady=5, width=15)
        salvar_btn.pack(side='left', padx=5, pady=5)

        vrlabel = tk.Label(config_frame, text="Versão Remota:", font=("Helvetica", 12), bg="#ffffff")
        vrlabel.pack(side='left', padx=5, pady=5)

        vr_entry = tk.Entry(config_frame, font=("Helvetica", 12), bd=1, relief=tk.SOLID)
        vr_entry.pack(side='left', padx=5, pady=5)
        vr_entry.insert(0, versao_REMOTA if versao_REMOTA else '')

        salvar_btn_versao = tk.Button(config_frame, text="Salvar Versão",
                                      command=partial(alterar_versao, caminho_arquivo_rede, vr_entry),
                                      font=("Helvetica", 12), bg="#2196F3", fg="white", bd=0, padx=10, pady=5, width=15)
        salvar_btn_versao.pack(side='left', padx=5, pady=5)

        config_frames.append(config_frame)

        config_frame.pack_forget()

    messagebox.showerror("Erro", f"Rede.txt não encontrado em: {' -  '.join(rede_inexistente)}")

    # Botão de configuração global
    config_button = tk.Button(root, text="CONFIG",
                              command=config_button_action,
                              font=("Helvetica", 12), bg="#FFC107", fg="black", bd=0, padx=10, pady=5, width=20)
    config_button.pack(pady=10)
def mostrar_ou_esconder_todas_configuracoes(config_frames, log_frame):
    for config_frame in config_frames:
        if config_frame.winfo_viewable():
            config_frame.pack_forget()  # Esconder configurações
        else:
            config_frame.pack(side='top', fill='x', padx=5, pady=5)  # Mostrar configurações
    if log_frame.winfo_viewable():
        log_frame.pack_forget()

    else:
        log_frame.pack(side='top', fill='x', padx=5, pady=5)  # Mostrar log
def atualizar_tela(root):
    # Código para recriar a tela aqui
    log_text.delete(1.0, tk.END)




root = tk.Tk()
root.title("HUB - ACSISTEMAS")
root.configure(bg="#fff")
root.geometry("400x400")
root.resizable(False, False)

log_frame = tk.Frame(root, bg="#e0e0e0")
log_text = tk.Text(log_frame, height=10, wrap='word', font=("Helvetica", 10))
log_text.pack(side='top', fill='x', padx=5, pady=5)
log_frame.pack_forget()

name_label = tk.Label(root, text="By:Caio Lira - Git:CaioLir4", bg="#fff", font=("Helvetica", 10))
name_label.pack(side='bottom', pady=10)

criar_botoes_atualizado(root)

btn_buscar_pastas = tk.Button(text="ATUALIZAR",
                                  font=("Helvetica", 12), bg="#FF5722", fg="white", bd=0, padx=10, pady=5, width=25,
                                  command=lambda: atualizar_tela(root))
btn_buscar_pastas.pack(pady=10)

root.mainloop()


