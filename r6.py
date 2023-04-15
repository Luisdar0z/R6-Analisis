import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import pandas as pd
import os
import numpy as np
import warnings
from datetime import datetime
from openpyxl import load_workbook
import random
warnings.simplefilter(action='ignore', category=FutureWarning)

fecha_actual = datetime.now()
fecha_formateada = fecha_actual.strftime('%Y-%m-%d')

def on_closing():
    window.quit()

def update_agent_info(*args):
    # Obtener los valores seleccionados
    selected_mode = mode_var.get()
    selected_map = map_var.get()
    selected_agent = agent_var.get()
    
    # Check if selected_agent is not empty
    if not selected_agent:
        return

    # Filtrar el DataFrame según los valores seleccionados
    if selected_mode == 'All' and selected_map == 'All':
        filtered_df = df
    elif selected_mode == 'All':
        filtered_df = df[df['Mapa'] == selected_map]
    elif selected_map == 'All':
        filtered_df = df[df['Modo de juego'] == selected_mode]
    else:
        filtered_df = df[(df['Modo de juego'] == selected_mode) & (df['Mapa'] == selected_map)]

    # Mostrar el nombre del agente seleccionado
    agent_name_label.config(text=selected_agent)

    # Mostrar la imagen del agente seleccionado
    image_path = os.path.join(os.path.dirname(file_path), f'{selected_agent}.png')
    if os.path.exists(image_path):
        image = Image.open(image_path)
        image.thumbnail((128, 128), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        agent_image_label.config(image=photo)
        agent_image_label.image = photo

    
    # Mostrar la suma de los valores del agente seleccionado
    agent_sum = filtered_df[selected_agent].replace('-', pd.NA).dropna().astype(int).sum()
    agent_wins = filtered_df[selected_agent].value_counts().get(1, 0)
    agent_lose = (agent_wins - agent_sum)
    agent_sum_label.config(text=f'El agente tiene {agent_wins} victorias\nEl agente tiene {agent_lose} derrotas\nCon un saldo de: {agent_sum}')
    

    # Mostrar cuántas veces aparece el agente con un valor válido
    agent_count = filtered_df[selected_agent].replace('-', pd.NA).dropna().count()
    agent_valid_count = filtered_df[selected_agent].replace(['-', 0], pd.NA).dropna().count()
    # count_percent = (agent_valid_count/agent_count)*100
    count_percent = np.divide(agent_valid_count, agent_count, where=agent_count!=0)*100
    if np.isnan(count_percent):
        count_percent = 0.00
    win_percent = np.divide(agent_wins, agent_valid_count, where=agent_valid_count!=0)*100
    if np.isnan(win_percent):
        win_percent = 0.00
    
    agent_count_label.config(text=f'Elegido {agent_valid_count} de {agent_count} veces, equivalente a un {count_percent:.2f}% de elegibilidad\nCon una tasa de victoria de {win_percent:.2f}%')

file_path = 'Data/agentes_r6.xlsx'

df = pd.read_excel(file_path, sheet_name='ToT')

# Crear una ventana para mostrar los datos
window = tk.Tk()
window.title('Rainbow Six Tool')
window.iconphoto(False, tk.PhotoImage(file='r6_ico.png'))
window.protocol("WM_DELETE_WINDOW", on_closing)

# Crear un cuaderno con dos pestañas
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Create a new tab for displaying game results
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Partidas')

# Add relevant code from r6.py to create the desired functionality in the new tab
dfa = pd.read_excel('Data/agentes_r6.xlsx', sheet_name='Agentes')
# Filter attacking and defending agents
atacantes = dfa[dfa['Tipo'] == 'Ataque']
defensores = dfa[dfa['Tipo'] == 'Defensa']

if len(atacantes) < 5 or len(defensores) < 5:
    print('No hay suficientes agentes atacantes o defensores')
else:
    # Selecciona aleatoriamente 5 agentes atacantes y 5 defensores
    atacantes_seleccionados = atacantes.sample(n=5)
    defensores_seleccionados = defensores.sample(n=5)
    
    # Calcula el tamaño del elemento más grande
    max_width = 0
    max_height = 0
    for index, row in atacantes_seleccionados.iterrows():
        imagen = Image.open('Data/' + row['Imagen'])
        max_width = max(max_width, imagen.width)
        max_height = max(max_height, imagen.height)
    for index, row in defensores_seleccionados.iterrows():
        imagen = Image.open('Data/' + row['Imagen'])
        max_width = max(max_width, imagen.width)
        max_height = max(max_height, imagen.height)
    # Crea dos listas vacías para almacenar las referencias a las etiquetas que contienen los nombres de los agentes atacantes y defensores
    atacantes_labels = []
    defensores_labels = []
    
    # Crea una lista con los posibles resultados del juego
    resultados = ['Victoria', 'Derrota', 'No jugado']
    
    # Crea objetos StringVar para almacenar los valores seleccionados en las listas desplegables de los agentes
    resultados_seleccionados = {}
    for index, row in atacantes_seleccionados.iterrows():
        resultados_seleccionados[row['Agente']] = tk.StringVar(tab3)
        resultados_seleccionados[row['Agente']].set(resultados[2])
    for index, row in defensores_seleccionados.iterrows():
        resultados_seleccionados[row['Agente']] = tk.StringVar(tab3)
        resultados_seleccionados[row['Agente']].set(resultados[2])
    
    def show_agent_options(agent_type, current_agent_index):
        # Obtener una lista de agentes disponibles del tipo especificado
        if agent_type == 'Ataque':
            available_agents = list(set(atacantes['Agente']) - set([label.cget('text') for label in atacantes_labels]))
        else:
            available_agents = list(set(defensores['Agente']) - set([label.cget('text') for label in defensores_labels]))
        
        # Cree una ventana de nivel superior para mostrar el menú desplegable
        toplevel = tk.Toplevel(tab3)
        
        # Crear un StringVar para almacenar el agente seleccionado
        selected_agent = tk.StringVar(toplevel)
        
        # Crear un OptionMenu para mostrar los agentes disponibles
        optionmenu = tk.OptionMenu(toplevel, selected_agent, *available_agents)
        optionmenu.pack()
        
        # Crear una función para actualizar el agente mostrado cuando el usuario hace una selección
        def update_agent():
            
            # Encuentre los widgets de etiqueta y botón para el agente actual
            if agent_type == 'Ataque':
                agent_label = atacantes_labels[current_agent_index]
            else:
                agent_label = defensores_labels[current_agent_index]
                
            for button in tab3.winfo_children():
                if isinstance(button, tk.Button) and hasattr(button, 'image'):
                    if button.grid_info()['row'] == agent_label.grid_info()['row'] - 1 and button.grid_info()['column'] == agent_label.grid_info()['column']:
                        agent_image_button = button
                        break
                    
            # Actualizar el nombre del agente mostrado
            new_agent = selected_agent.get()
            agent_label.config(text=new_agent)
            
            # Actualice la imagen del agente que se muestra
            image_path = os.path.join(os.path.dirname(file_path), f'{new_agent}.png')
            if os.path.exists(image_path):
                image = Image.open(image_path)
                photo = ImageTk.PhotoImage(image)
                agent_image_button.config(image=photo)
                agent_image_button.image = photo
                
            # Cerrar la ventana de nivel superior
            toplevel.destroy()
            
        # Cree un botón para actualizar el agente que se muestra cuando se hace clic
        button = tk.Button(toplevel, text='OK', command=update_agent)
        button.pack()
                        
    def create_show_agent_options_callback(agent_type, current_agent_index):
        def callback():
            show_agent_options(agent_type, current_agent_index)
        return callback
    
    # Muestra las imágenes y los nombres de los agentes seleccionados en la ventana utilizando grid
    tk.Label(tab3, text='Ataque', background='#4682b4').grid(row=0, columnspan=6, sticky='ew')
    for i, (index, row) in enumerate(atacantes_seleccionados.iterrows()):
        
        imagen = Image.open('Data/' + row['Imagen'])
        photo = ImageTk.PhotoImage(imagen)
        button = tk.Button(tab3, image=photo, highlightbackground='blue', highlightthickness=2, width=max_width, height=max_height,
                    command=create_show_agent_options_callback('Ataque', i))
        button.image = photo
        button.grid(row=1, column=i)
        tk.Label(tab3, text=row['Agente']).grid(row=2, column=i)
        # Crea una etiqueta para mostrar el nombre del agente atacante y almacena una referencia a la etiqueta en la lista atacantes_labels
        label = tk.Label(tab3, text=row['Agente'])
        label.grid(row=2, column=i)
        atacantes_labels.append(label)
        tk.OptionMenu(tab3, resultados_seleccionados[row['Agente']], *resultados).grid(row=3, column=i)

    tk.Label(tab3).grid(row=4, columnspan=6, sticky='ew')
    tk.Label(tab3, text='Defensa', background='#5cb85c').grid(row=5, columnspan=6, sticky='ew')
    for i, (index, row) in enumerate(defensores_seleccionados.iterrows()):
        
        imagen = Image.open('Data/' + row['Imagen'])
        photo = ImageTk.PhotoImage(imagen)
        button = tk.Button(tab3, image=photo, highlightbackground='green', highlightthickness=2, width=max_width, height=max_height,
                    command=create_show_agent_options_callback('Defensa', i))
        button.image = photo
        button.grid(row=6, column=i)
        tk.Label(tab3, text=row['Agente']).grid(row=7, column=i)
        # Crea una etiqueta para mostrar el nombre del agente defensor y almacena una referencia a la etiqueta en la lista defensores_labels
        label = tk.Label(tab3, text=row['Agente'])
        label.grid(row=7, column=i)
        defensores_labels.append(label)
        tk.OptionMenu(tab3, resultados_seleccionados[row['Agente']], *resultados).grid(row=8, column=i)
        
    # Carga la hoja Mapas del archivo xlsx en un DataFrame de pandas
    mapas_df = pd.read_excel('Data/agentes_r6.xlsx', sheet_name='Mapas')
    
    # Crea una lista con los nombres de los mapas
    mapas = mapas_df['Mapa'].tolist()
    modos = mapas_df['Modos'].dropna().tolist()
    
    # Crea un objeto StringVar para almacenar el valor seleccionado en la lista desplegable
    mapa_seleccionado = tk.StringVar(tab3)
    modo_seleccionado = tk.StringVar(tab3)
    
    # Establece el valor inicial de la lista desplegable como el primer elemento de la lista de mapas
    mapa_seleccionado.set(mapas[0])
    modo_seleccionado.set(modos[0])
    
    tk.Label(tab3).grid(row=9, columnspan=6, sticky='ew')
    tk.Label(tab3, text='Parámetros', background='#ec6681').grid(row=10, columnspan=6, sticky='ew')
    
    # Agrega una etiqueta de texto a la izquierda de la lista desplegable
    tk.Label(tab3, text='Mapas:').grid(row=11, column=1)
    tk.Label(tab3, text='Modos:').grid(row=12, column=1)
    
    # Crea una lista desplegable con los nombres de los mapas utilizando OptionMenu
    tk.OptionMenu(tab3, mapa_seleccionado, *mapas).grid(row=11, column=3)
    tk.OptionMenu(tab3, modo_seleccionado, *modos).grid(row=12, column=3)
    
    # Define una función para imprimir el valor seleccionado en la lista desplegable al cerrar la ventana        
    def guardar():
        # Crea un diccionario para mapear los estados a valores numéricos
        estado_a_valor = {'Victoria': 1, 'Derrota': -1, 'No jugado': 0}
        
        # Crea un diccionario para almacenar los valores de los agentes
        agentes = {}
        
        for agente in resultados_seleccionados:
            resultado = resultados_seleccionados[agente].get()
            # Agrega el valor del agente al diccionario
            agentes[agente] = estado_a_valor[resultado]
        
        partidas_df = pd.read_excel('Data/agentes_r6.xlsx', sheet_name='ToT')
        
        if partidas_df['Fecha'].isnull().any():
            # Encuentra la primera celda vacía en la columna 'Fecha'
            fila = partidas_df['Fecha'].isnull().idxmax()

            # Guarda la fecha en la celda encontrada
            partidas_df.at[fila, 'Fecha'] = fecha_formateada
            
            # Guarda el modo de juego en la celda encontrada
            partidas_df.at[fila, 'Modo de juego'] = modo_seleccionado.get()
            
            # Guarda el nombre del mapa en la celda encontrada
            partidas_df.at[fila, 'Mapa'] = mapa_seleccionado.get()
            
            # Guarda los valores de los agentes en las columnas con el nombre del agente
            for agente in df['Agente']:
                if agente in agentes:
                    partidas_df.at[fila, agente] = agentes[agente]
                else:
                    partidas_df.at[fila, agente] = '-'
            # Aplica la fórmula a la columna "W/L"
            fila_excel = fila + 2
            formula = f'=IF((SUM(D{fila_excel}:BR{fila_excel}))>=1,"Victoria",IF((SUM(D{fila_excel}:BR{fila_excel}))<0,"Derrota",""))'
            partidas_df.at[fila, 'W/L'] = formula
        else:
            # Agrega una nueva fila al final del DataFrame con la fecha en la columna 'Fecha'
            nueva_fila = {'Fecha': fecha_formateada}
            
            # Agrega el modo de juego a la nueva fila
            nueva_fila['Modo de juego'] = modo_seleccionado.get()
            
            # Agrega el nombre del mapa a la nueva fila
            nueva_fila['Mapa'] = mapa_seleccionado.get()
            
            # Agrega los valores de los agentes a la nueva fila
            for agente in dfa['Agente']:
                if agente in agentes:
                    nueva_fila[agente] = agentes[agente]
                else:
                    nueva_fila[agente] = '-'
            
            partidas_df = partidas_df.append(nueva_fila, ignore_index=True)
            
            # Aplica la fórmula a la columna "W/L"
            fila_excel = len(partidas_df) + 1
            formula = f'=IF((SUM(D{fila_excel}:BR{fila_excel}))>=1,"Victoria",IF((SUM(D{fila_excel}:BR{fila_excel}))<0,"Derrota",""))'
            partidas_df.at[len(partidas_df)-1, 'W/L'] = formula
        # Carga el libro de trabajo existente
        book = load_workbook('Data/agentes_r6.xlsx')
        
        # Crea un escritor de pandas ExcelWriter utilizando openpyxl como motor
        writer = pd.ExcelWriter('Data/agentes_r6.xlsx', engine='openpyxl')
        
        # Asigna el libro de trabajo al escritor
        writer.book = book
        
        # Guarda el DataFrame partidas_df en la hoja 'Partidas' del libro de trabajo
        partidas_df.to_excel(writer, sheet_name='ToT', index=False)
        print("Guardado")
        # Guarda los cambios en el archivo xlsx
        writer.save()
        
    def resetear():
        # Elimina todos los widgets de la ventana
        for widget in tab3.winfo_children():
            widget.destroy()
        
        # Crea los widgets nuevamente
             
        # Selecciona aleatoriamente 5 agentes atacantes y 5 defensores
        atacantes_seleccionados = atacantes.sample(n=5)
        defensores_seleccionados = defensores.sample(n=5)
        
        # Crea un nuevo diccionario para almacenar los valores seleccionados en las listas desplegables de los agentes
        global resultados_seleccionados
        resultados_seleccionados = {}
        for index, row in atacantes_seleccionados.iterrows():
            resultados_seleccionados[row['Agente']] = tk.StringVar(tab3)
            resultados_seleccionados[row['Agente']].set(resultados[2])
        for index, row in defensores_seleccionados.iterrows():
            resultados_seleccionados[row['Agente']] = tk.StringVar(tab3)
            resultados_seleccionados[row['Agente']].set(resultados[2])
        
        # Limpiar las listas atacantes_labels y defensores_labels
        atacantes_labels.clear()
        defensores_labels.clear()
        
        def show_agent_options(agent_type, current_agent_index):
            # Obtener una lista de agentes disponibles del tipo especificado
            if agent_type == 'Ataque':
                available_agents = list(set(atacantes['Agente']) - set([label.cget('text') for label in atacantes_labels]))
            else:
                available_agents = list(set(defensores['Agente']) - set([label.cget('text') for label in defensores_labels]))
            
            # Cree una ventana de nivel superior para mostrar el menú desplegable
            toplevel = tk.Toplevel(tab3)
            
            # Crear un StringVar para almacenar el agente seleccionado
            selected_agent = tk.StringVar(toplevel)
            
            # Crear un OptionMenu para mostrar los agentes disponibles
            optionmenu = tk.OptionMenu(toplevel, selected_agent, *available_agents)
            optionmenu.pack()
            
            # Crear una función para actualizar el agente mostrado cuando el usuario hace una selección
            def update_agent():
                
                # Encuentre los widgets de etiqueta y botón para el agente actual
                if agent_type == 'Ataque':
                    agent_label = atacantes_labels[current_agent_index]
                else:
                    agent_label = defensores_labels[current_agent_index]
                    
                for button in tab3.winfo_children():
                    if isinstance(button, tk.Button) and hasattr(button, 'image'):
                        if button.grid_info()['row'] == agent_label.grid_info()['row'] - 1 and button.grid_info()['column'] == agent_label.grid_info()['column']:
                            agent_image_button = button
                            break
                        
                # Actualizar el nombre del agente mostrado
                new_agent = selected_agent.get()
                agent_label.config(text=new_agent)
                
                # Actualice la imagen del agente que se muestra
                image_path = os.path.join(os.path.dirname(file_path), f'{new_agent}.png')
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    photo = ImageTk.PhotoImage(image)
                    agent_image_button.config(image=photo)
                    agent_image_button.image = photo
                    
                # Cerrar la ventana de nivel superior
                toplevel.destroy()
                
            # Cree un botón para actualizar el agente que se muestra cuando se hace clic
            button = tk.Button(toplevel, text='OK', command=update_agent)
            button.pack()
                            
        
        def create_show_agent_options_callback(agent_type, current_agent_index):
            def callback():
                show_agent_options(agent_type, current_agent_index)
            return callback
        
        # Muestra las imágenes y los nombres de los agentes seleccionados en la ventana utilizando grid
        tk.Label(tab3, text='Ataque', background='#4682b4').grid(row=0, columnspan=6, sticky='ew')
        for i, (index, row) in enumerate(atacantes_seleccionados.iterrows()):
            
            imagen = Image.open('Data/' + row['Imagen'])
            photo = ImageTk.PhotoImage(imagen)
            button = tk.Button(tab3, image=photo, highlightbackground='blue', highlightthickness=2, width=max_width, height=max_height,
                        command=create_show_agent_options_callback('Ataque', i))
            button.image = photo
            button.grid(row=1, column=i)
            tk.Label(tab3, text=row['Agente']).grid(row=2, column=i)
            # Crea una etiqueta para mostrar el nombre del agente atacante y almacena una referencia a la etiqueta en la lista atacantes_labels
            label = tk.Label(tab3, text=row['Agente'])
            label.grid(row=2, column=i)
            atacantes_labels.append(label)
            tk.OptionMenu(tab3, resultados_seleccionados[row['Agente']], *resultados).grid(row=3, column=i)

        tk.Label(tab3).grid(row=4, columnspan=6, sticky='ew')
        tk.Label(tab3, text='Defensa', background='#5cb85c').grid(row=5, columnspan=6, sticky='ew')
        for i, (index, row) in enumerate(defensores_seleccionados.iterrows()):
            
            imagen = Image.open('Data/' + row['Imagen'])
            photo = ImageTk.PhotoImage(imagen)
            button = tk.Button(tab3, image=photo, highlightbackground='green', highlightthickness=2, width=max_width, height=max_height,
                        command=create_show_agent_options_callback('Defensa', i))
            button.image = photo
            button.grid(row=6, column=i)
            tk.Label(tab3, text=row['Agente']).grid(row=7, column=i)
            # Crea una etiqueta para mostrar el nombre del agente defensor y almacena una referencia a la etiqueta en la lista defensores_labels
            label = tk.Label(tab3, text=row['Agente'])
            label.grid(row=7, column=i)
            defensores_labels.append(label)
            tk.OptionMenu(tab3, resultados_seleccionados[row['Agente']], *resultados).grid(row=8, column=i)
        
        print("Reseteo")
        # Crea una lista con los nombres de los mapas y modos
        mapas = mapas_df['Mapa'].tolist()
        modos = mapas_df['Modos'].dropna().tolist()
        
        # Reinicia los valores de las listas desplegables
        mapa_seleccionado.set(mapas[0])
        modo_seleccionado.set(modos[0])
        
        tk.Label(tab3).grid(row=9, columnspan=6, sticky='ew')
        tk.Label(tab3, text='Parámetros', background='#ec6681').grid(row=10, columnspan=6, sticky='ew')
        
        # Agrega una etiqueta de texto a la izquierda de la lista desplegable
        tk.Label(tab3, text='Mapas:').grid(row=11, column=1)
        tk.Label(tab3, text='Modos:').grid(row=12, column=1)
        
        # Crea una lista desplegable con los nombres de los mapas utilizando OptionMenu
        tk.OptionMenu(tab3, mapa_seleccionado, *mapas).grid(row=11, column=3)
        tk.OptionMenu(tab3, modo_seleccionado, *modos).grid(row=12, column=3)
        
        tk.Label(tab3).grid(row=13, columnspan=6, sticky='ew')
        tk.Label(tab3, text='Opciones', background='#8b98e8').grid(row=14, columnspan=6, sticky='ew')
        
        # Crea un botón para guardar los datos en el archivo xlsx sin cerrar la ventana
        tk.Button(tab3,text='Guardar',command=guardar).grid(row=15,column=1)
        
        # Crea un botón para reiniciar todos los valores de la ventana y volver a elegir agentes de manera aleatoria
        tk.Button(tab3, text='Resetear', command=resetear).grid(row=15, column=3)
    
    tk.Label(tab3).grid(row=13, columnspan=6, sticky='ew')
    tk.Label(tab3, text='Opciones', background='#8b98e8').grid(row=14, columnspan=6, sticky='ew')
        
    # Crea un botón para reiniciar todos los valores de la ventana y volver a elegir agentes de manera aleatoria
    tk.Button(tab3, text='Resetear', command=resetear).grid(row=15, column=3)
    # Crea un botón para guardar los datos en el archivo xlsx sin cerrar la ventana
    tk.Button(tab3, text='Guardar', command=guardar).grid(row=15, column=1)
    
    
# Crear la primera pestaña ("Tabla General")
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Tabla General')

# Crear un contenedor para la tabla y la barra deslizante
table_container = tk.Frame(tab1)
table_container.pack(fill='both', expand=True)


# Crear una tabla para mostrar los datos
table = tk.Canvas(table_container)
table.pack(side='left', fill='both', expand=True)

# Agregar una barra deslizante horizontal
scrollbar = ttk.Scrollbar(tab1, orient='horizontal', command=table.xview)
scrollbar.pack(side='bottom', fill='x')
table.configure(xscrollcommand=scrollbar.set)

# Crear un marco para contener las celdas de la tabla
table_frame = tk.Frame(table)
table.create_window(0, 0, window=table_frame, anchor='nw')


def recargar():
    # Read the data from the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name='ToT')
    # Agregar encabezados de columna
    
    for col, column in enumerate(df.columns):
        header = tk.Label(table_frame, text=column, font=('Arial', 12, 'bold'))
        header.grid(row=0, column=col)

    # Agregar datos a la tabla
    for row in range(len(df)):
        for col, column in enumerate(df.columns):
            cell = tk.Label(table_frame, text=df.iloc[row][column])
            cell.grid(row=row+1, column=col)

# Agregar encabezados de columna
for col, column in enumerate(df.columns):
    header = tk.Label(table_frame, text=column, font=('Arial', 12, 'bold'))
    header.grid(row=0, column=col)

# Agregar datos a la tabla
for row in range(len(df)):
    for col, column in enumerate(df.columns):
        cell = tk.Label(table_frame, text=df.iloc[row][column])
        cell.grid(row=row+1, column=col)

# Actualizar el tamaño de la región de desplazamiento
table.update_idletasks()
table.configure(scrollregion=table.bbox('all'))

# Create a "Recargar" button in the "Tabla General" tab
recargar_button = tk.Button(tab1, text='Recargar', command=recargar)
recargar_button.pack()

# Crear la segunda pestaña ("Análisis")
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Análisis')



# Crear listas desplegables para seleccionar el modo de juego, el mapa y el agente
mode_label = tk.Label(tab2, text='Modos de Juego')
mode_label.pack()
mode_var = tk.StringVar()
mode_dropdown = ttk.Combobox(tab2, textvariable=mode_var, values=['All'] + list(df['Modo de juego'].unique()))
mode_dropdown.pack()

map_label = tk.Label(tab2, text='Mapas')
map_label.pack()
map_var = tk.StringVar()
map_dropdown = ttk.Combobox(tab2, textvariable=map_var, values=['All'] + list(df['Mapa'].unique()))
map_dropdown.pack()

agent_label = tk.Label(tab2, text='Agentes')
agent_label.pack()
agent_var = tk.StringVar()
agent_dropdown = ttk.Combobox(tab2, textvariable=agent_var, values=list(df.columns[3:]))
agent_dropdown.pack()

def reload_data():
    global df
    df = pd.read_excel(file_path, sheet_name='ToT')
    mode_dropdown['values'] = ['All'] + list(df['Modo de juego'].unique())
    map_dropdown['values'] = ['All'] + list(df['Mapa'].unique())
    agent_dropdown['values'] = list(df.columns[3:])
    mode_var.trace('w', update_agent_info)
    map_var.trace('w', update_agent_info)
    agent_var.trace('w', update_agent_info)

# Crear un contenedor para mostrar información sobre el agente seleccionado
agent_info_container = tk.Frame(tab2)
agent_info_container.pack()

# Mostrar el nombre del agente seleccionado
agent_name_label = tk.Label(agent_info_container, font=('Arial', 12, 'bold'))
agent_name_label.pack()

# Mostrar la imagen del agente seleccionado
agent_image_label = tk.Label(agent_info_container)
agent_image_label.pack()

# Mostrar la suma de los valores del agente seleccionado
agent_sum_label = tk.Label(agent_info_container)
agent_sum_label.pack()

# Mostrar cuántas veces aparece el agente con un valor válido
agent_count_label = tk.Label(agent_info_container)
agent_count_label.pack()

# Actualizar la información del agente cuando se cambie la selección
mode_var.trace('w', update_agent_info)
map_var.trace('w', update_agent_info)
agent_var.trace('w', update_agent_info)

# Create a "Recargar" button in the "Tabla General" tab
recargar_button2 = tk.Button(tab2, text='Recargar', command=reload_data)
recargar_button2.pack()

window.mainloop()