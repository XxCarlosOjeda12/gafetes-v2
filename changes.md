

📄 Archivo: directores_procesados.xlsx

Se agrega la columna Numeracion para mantener ordenados los PDF al distribuir.

🐍 Archivo: excel.py

Se agrega la lectura de la columna Numeracion.

🐍 Archivo: generator.py

Se agrega numeración al nombrar los archivos de usuario y acompañante.

⚙️ Orden de Ejecución
🧩 Generar los PDF
python gafetes_generator.py --excel directores_procesados.xlsx --qr-strategy cache --output-dir gaf

📐 Escalado de los PDF

Lee la carpeta origen y genera versiones escaladas en la carpeta de destino:

python procesar_carpeta.py "./gafetes_directores" "./gafetes_directores_escala"

🧾 Generar lista JSON ordenada

Lee los archivos escalados y crea un JSON con el orden en que se generará el tabloide:

python generar_lista.py ./gafetes_directores_escala gafetes_directores_escala.json

🗞️ Generar el tabloide final

Usa el JSON de entrada (que contiene los pares de archivos en orden de ejecución) para crear el PDF final:

python distribuir_final.py gafetes_directores_escala.json gafetes_directores_29oct.pdf --dpi 300


pip install pdf2image pillow --break-system-packages

instalar poppler-25.07.0
