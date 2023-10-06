from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
import csv
import requests
from bs4 import BeautifulSoup
import io
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
from .models import Urls


def get_urls(url):
    """
    Fetches the URLs for PDF files from the given URL directory.

    Args:
        url (str): The URL of the directory containing PDF files.

    Returns:
        list: A list of URLs for the PDF files found in the directory.
    """
    urls_list = []
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    # Getting the list of available URLs for PDF files in the given directory
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf') and not href.endswith('/.pdf'):
            if not href.startswith('http'):
                absolute_url = urljoin(url, href)
            urls_list.append(absolute_url)

    return urls_list


def extract_text_from_remote_pdf(url, target_word):
    """
    Extracts text from a remote PDF file and checks if it contains the target word.

    Args:
        url (str): The URL of the remote PDF file.
        target_word (str): The word to search for in the PDF file.

    Returns:
        Tuple[List[int], int, bool]: A tuple containing a list of page occurrences, count, and a boolean indicating if the target word is found.
    """
    occurrences = []
    count = 0

    response = requests.get(url, stream=True)
    pdf_file = response.content
    try:
        with io.BytesIO(pdf_file) as file_obj:
            reader = PdfReader(file_obj)
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and target_word.lower() in text.lower():
                    occurrences.append(page_number)
                    count += text.lower().count(target_word.lower())
        if occurrences:
            return occurrences, count, True
    except:
        pass

    return occurrences, count, False


def export_to_csv(modeladmin, request, queryset):
    start_time = time.time()  # Start time

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_urls.csv"'
    writer = csv.writer(response)
    writer.writerow(['URL', 'Keyword', 'Page Numbers', 'Count', 'Keyword Found'])

    # Use a session object for making requests
    session = requests.Session()

    progress_interval = 10  # Update progress every 10%
    progress = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url_obj in queryset:
            target_word = url_obj.keyword
            url = url_obj.Url
            urls = get_urls(url)

            results = []
            for s_url in urls:
                # Start extracting text from each URL as soon as it is parsed
                result = executor.submit(extract_text_from_remote_pdf, s_url, target_word)
                results.append((s_url, result))

            c = 0
            for url, result in results:
                occurrences, count, found = result.result()
                writer.writerow([url, target_word, occurrences, count, str(found)])
                c += 1
                print(url,target_word,occurrences,count,str(found),c)

                # Calculate and send progress update
                new_progress = int((c / len(results)) * 100)
                if new_progress >= progress + progress_interval:
                    progress = new_progress
                    messages.info(request, f"Processing: {progress}% complete")
                    request.session['progress'] = progress  # Store progress in session

    end_time = time.time()  # End time
    runtime = end_time - start_time
    print(f"Runtime: {runtime} seconds")

    messages.info(request, "Processing: 100% complete")
    request.session['progress'] = 100  # Store 100% progress in session

    return response


class UrlsAdmin(admin.ModelAdmin):
    list_display = ['id', 'Url', 'keyword']
    ordering = ['id']
    actions = [export_to_csv]


admin.site.register(Urls, UrlsAdmin)
