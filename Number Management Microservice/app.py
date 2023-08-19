from flask import Flask, request, render_template
import concurrent.futures
import requests

app = Flask(__name__)

def fetch_numbers_from_url(url):
    try:
        response = requests.get(url, timeout=5)  
        if response.status_code == 200:
            data = response.json()
            return data.get("numbers", [])
    except requests.exceptions.Timeout:
        pass 
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
    return []

def merge_and_sort_numbers(numbers_lists):
    merged_numbers = set()
    for numbers in numbers_lists:
        merged_numbers.update(numbers)
    return sorted(list(merged_numbers))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        urls = request.form.getlist('url')
        numbers_lists = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_numbers_from_url, url) for url in urls]
            for future in concurrent.futures.as_completed(futures):
                numbers = future.result()
                if numbers:
                    numbers_lists.append(numbers)

        merged_numbers = merge_and_sort_numbers(numbers_lists)

        return render_template('index.html', numbers=merged_numbers, input_urls=urls)
    
    return render_template('index.html', numbers=[], input_urls=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)
