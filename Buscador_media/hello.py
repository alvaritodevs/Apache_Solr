import requests
from flask import Flask, request, jsonify, send_file, render_template
from sugerencias import sugerencias_inteligentes
import os
import json
import csv


app = Flask(__name__)


PRODUCTOS = []

with open("data/amazon_products.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        PRODUCTOS.append(row)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_products():
    products = []
    with open("data/amazon_products.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products.append({
                "title": row["title"],
                "imgUrl": row["imgUrl"],
                "price": row.get("price", "N/A")
            })
    return products

@app.route("/")
def index():

    return """
    <!DOCTYPE html>
    <html>
    <head>

        <style>
        @font-face {
            font-family: 'Oblique';
            src: url("/static/Oblique.otf") format("opentype");
            font-weight: normal;
            font-style: normal;
        }

        body {
            font-family: 'Oblique', sans-serif!important;
        }
        </style>

        <link href="https://unpkg.com/filepond@^4/dist/filepond.css" rel="stylesheet" />
        <script src="https://cdn.tailwindcss.com"></script>


    </head>
    <body class="p-10 bg-gray-100">
        
        <nav class="bg-white border-gray-200 dark:bg-gray-900 rounded-xl">
        <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
        <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
            <img src="/static/img/Media_Markt_logo.png" class="h-8" alt="Flowbite Logo" />
        </a>

        <div class="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-search">
            <div class="relative mt-3 md:hidden">
                <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">

                </div>
                <input type="text" id="search-navbar" class="block w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Search...">
            </div>
            <ul class="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
                <li>
                <a href="#" class="block py-2 px-3 text-white bg-red-700 rounded-sm md:bg-transparent md:text-red-700 md:p-0 md:dark:text-red-500" aria-current="page">Home</a>
                </li>
                <li>
                <a href="#" class="block py-2 px-3 text-gray-900 rounded-sm hover:bg-gray-100 md:hover:bg-transparent md:hover:text-red-700 md:p-0 md:dark:hover:text-red-500 dark:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">About</a>
                </li>
                <li>
                <a href="#" class="block py-2 px-3 text-gray-900 rounded-sm hover:bg-gray-100 md:hover:bg-transparent md:hover:text-red-700 md:p-0 dark:text-white md:dark:hover:text-ref-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">Services</a>
                </li>
            </ul>
        </div>

        <div class="flex md:order-2">
            <button type="button" data-collapse-toggle="navbar-search" aria-controls="navbar-search" aria-expanded="false" class="md:hidden text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-sm p-2.5 me-1">
            <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
            </svg>
            <span class="sr-only">Search</span>
            </button>
            <div class="relative hidden md:block">

            <input type="text" id="search-box" placeholder="Buscar producto..." class="w-full max-w-md px-4 py-2 border border-gray-300 rounded-md focus:outline-none">
            </div>
            <button data-collapse-toggle="navbar-search" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-search" aria-expanded="false">
                <span class="sr-only">Open main menu</span>
                <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
                </svg>
            </button>
        </div>

        </div>
        </nav>




        <div id="results" class="mt-4 space-y-3"></div>

        <script>
        let controller = null;

        document.getElementById('search-box').addEventListener('input', async (e) => {
        const query = e.target.value.trim();

        if (controller) controller.abort();
        controller = new AbortController();

        if (query === "") {
            document.getElementById('results').innerHTML = "";
            return;
        }

        try {
            const res = await fetch(`/solr-search?q=${encodeURIComponent(query)}`, {
            signal: controller.signal
            });

            const data = await res.json();

            const list = document.getElementById('results');
            list.innerHTML = "";

            data.forEach(item => {
            const line = document.createElement("div");
            line.className = "flex items-center bg-white rounded-lg shadow-sm p-3 gap-3 hover:shadow transition";

            line.innerHTML = `
                <img src="${item.imgUrl || 'https://via.placeholder.com/60'}"
                    alt="${item.title}"
                    class="w-14 h-14 object-cover rounded-md flex-shrink-0" />

                <div class="flex-1 overflow-hidden">
                <a href="${item.productURL}"
                    target="_blank"
                    class="block text-sm font-medium text-gray-900 hover:underline truncate">
                    ${item.title}
                </a>

                <div class="text-xs text-yellow-500 mt-0.5">
                    ⭐ ${item.stars || 'N/A'}
                    <span class="text-gray-500 ml-2">
                    (${item.reviews || 0} reviews)
                    </span>
                </div>

                <div class="text-sm text-red-600 font-bold mt-1">
                    $${item.price || 'N/A'}
                </div>
                </div>
            `;

            list.appendChild(line);
            });

        } catch (err) {
            if (err.name !== "AbortError") {
            console.error("Error:", err);
            }
        }
        });
        </script>



        <div class="max-w-7xl mx-auto">
            
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">

            <!-- iPhone 15 Pro -->
            <div class="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col">
                <img src="https://static.fnac-static.com/multimedia/Images/ES/NR/a7/44/78/7881895/1541-3.jpg" alt="iPhone 15 Pro" class="w-full h-48 object-cover rounded-lg mb-4">
                <h2 class="text-md font-semibold text-gray-900 mb-2">iPhone 15 Pro - 128GB - Natural Titanium</h2>
                <div class="text-lg font-bold text-red-600">$999.00</div>
                <div class="text-sm text-gray-400 line-through mb-4">$1099.00</div>
                <button class="mt-auto bg-black text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition">Add to Cart</button>
            </div>

            <!-- iPhone 14 -->
            <div class="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col">
                <img src="https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-model-unselect-gallery-1-202309?wid=5120&hei=2880&fmt=jpeg&qlt=80&.v=1692915954271" alt="iPhone 14" class="w-full h-48 object-cover rounded-lg mb-4">
                <h2 class="text-md font-semibold text-gray-900 mb-2">iPhone 14 - 128GB - Midnight</h2>
                <div class="text-lg font-bold text-red-600">$699.00</div>
                <div class="text-sm text-gray-400 line-through mb-4">$799.00</div>
                <button class="mt-auto bg-black text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition">Add to Cart</button>
            </div>

            <!-- iPhone 13 Mini -->
            <div class="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKEpvTbq1QpUqZ4aHWit2Epc4Qb-lubmfiJg&s" alt="iPhone 13 Mini" class="w-full h-48 object-cover rounded-lg mb-4">
                <h2 class="text-md font-semibold text-gray-900 mb-2">iPhone 13 Mini - 128GB - Pink</h2>
                <div class="text-lg font-bold text-red-600">$599.00</div>
                <div class="text-sm text-gray-400 line-through mb-4">$699.00</div>
                <button class="mt-auto bg-black text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition">Add to Cart</button>
            </div>

            <!-- iPhone SE (3rd Gen) -->
            <div class="bg-white rounded-2xl shadow-md hover:shadow-lg transition p-4 flex flex-col">
                <img src="https://compasia.com.ph/cdn/shop/files/iphone-14-pro-711452.png?v=1737456754" alt="iPhone SE" class="w-full h-48 object-cover rounded-lg mb-4">
                <h2 class="text-md font-semibold text-gray-900 mb-2">iPhone SE (3rd Gen) - 64GB - Starlight</h2>
                <div class="text-lg font-bold text-red-600">$429.00</div>
                <div class="text-sm text-gray-400 line-through mb-4">$499.00</div>
                <button class="mt-auto bg-black text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition">Add to Cart</button>
            </div>

            </div>
        </div>

        <input id="file-upload" type="file" name="file" class="filepond filesuu" multiple data-allow-reorder="true" />

        <script src="https://unpkg.com/filepond@^4/dist/filepond.js"></script>
        <script src="https://unpkg.com/filepond-plugin-image-exif-orientation/dist/filepond-plugin-image-exif-orientation.js"></script>
        <script src="https://unpkg.com/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.js"></script>
        <script src="https://unpkg.com/filepond-plugin-file-validate-size/dist/filepond-plugin-file-validate-size.js"></script>
        <script src="https://unpkg.com/filepond-plugin-image-edit/dist/filepond-plugin-image-edit.js"></script>

        <script>

            document.addEventListener('DOMContentLoaded', function() {

                FilePond.registerPlugin(
                FilePondPluginImagePreview,
                FilePondPluginImageExifOrientation,
                FilePondPluginFileValidateSize,
                FilePondPluginImageEdit
                );

            FilePond.create(document.querySelector('.filesuu'), {
                server: {
                process: {
                    url: '/upload',       // your Flask endpoint
                    method: 'POST',
                    withCredentials: false,
                    headers: {},
                    timeout: 7000,
                    onload: (response) => {
                    console.log('Upload complete:', response);
                    },
                    onerror: (response) => {
                    console.error('Upload failed:', response);
                    }
                },
                },
                allowProcess: true,           // Enable processing (upload)
                instantUpload: true,          // Upload immediately after file drop
                allowMultiple: false,
                maxFileSize: '500MB',
                labelIdle: 'Drag & drop or <span class="filepond--label-action">Browse</span> your file',
            });

            });   

        </script>

    </body>
    </html>
    """




@app.route('/sugerencias')
def sugerencias():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])

    sugerencias_filtradas = [
        p for p in PRODUCTOS if query in p['title'].lower()
    ]

    if not sugerencias_filtradas and 'sugerencias_inteligentes' in globals():
        sugerencias_filtradas = sugerencias_inteligentes(query)

    return jsonify([p['title'] for p in sugerencias_filtradas[:5]])

@app.route("/promociones")
def promociones():
    with open("data/promociones.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, 'saved.json'))
        return 'success', 200
    return 'no file', 400

SOLR_URL = "http://localhost:8983/solr/apache/select"

@app.route('/solr-search')
def solr_search():
    query = request.args.get("q", "").strip()

    params = {
        "q": query,                           # Búsqueda flexible
        "rows": 10,
        "wt": "json",
        "defType": "edismax",
        "qf": "title",
    }

    try:
        solr_response = requests.get(SOLR_URL, params=params)
        solr_response.raise_for_status()

        docs = solr_response.json().get("response", {}).get("docs", [])

        # Puedes imprimir para depurar:
        # print("DOCS:", docs)

        results = []
        for doc in docs:
            results.append({
                "title": doc.get("title", ""),
                "imgUrl": doc.get("imgUrl", ""),
                "productURL": doc.get("productURL", ""),
                "stars": doc.get("stars", ""),
                "reviews": doc.get("reviews", ""),
                "price": doc.get("price", ""),
                "asin": doc.get("asin", "")
            })

        return jsonify(results)

    except Exception as e:
        print("Error consultando Solr:", e)
        return jsonify([]), 500