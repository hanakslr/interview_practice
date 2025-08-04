from concurrent.futures import ProcessPoolExecutor
from queue import Queue
from urllib.parse import urlparse
from threading import Lock, Thread

from crawler.url_worker import UrlWorker

MAX_WORKERS = 5


class CrawlerQueue:
    def __init__(self):
        self.to_visit = Queue()
        self.seen_urls = set()
        self.seen_urls_lock = Lock()

    def add_urls(self, urls):
        with self.seen_urls_lock:
            for url in urls:
                if url not in self.seen_urls:
                    self.seen_urls.add(url)
                    self.to_visit.put(url)

    def get_next_url(self) -> str | None:
        return self.to_visit.get()

    def task_done(self):
        # We finished something
        self.to_visit.task_done()


def crawler_worker(cq: CrawlerQueue):
    while True:
        url = cq.get_next_url()

        if not url:
            print("Shutting down")
            break

        found_urls = UrlWorker(url).run()
        cq.add_urls(found_urls)
        cq.task_done()


def crawl(starting_url):
    cq = CrawlerQueue()
    cq.add_urls([starting_url])

    threads = []
    for _ in range(MAX_WORKERS):
        t = Thread(target=crawler_worker, args=(cq,))
        t.start()
        threads.append(t)

    # Block until there are no more tasks to do
    cq.to_visit.join()

    # Shutdown each of our threads putting in a sentinel
    for _ in threads:
        cq.to_visit.put(None)

    # Block until all threads are nicely shutdown
    for t in threads:
        t.join()

    return len(cq.seen_urls)


def multicrawl():
    starting_urls = ["https://arrow4graphics.com", "https://getpetaler.com"]

    with ProcessPoolExecutor(MAX_WORKERS) as exec:
        results = exec.map(crawl, starting_urls)

    for i, res in enumerate(results):
        print(f"For {starting_urls[i]} found {res} urls.")


if __name__ == "__main__":
    multicrawl()
    print("Done!")
