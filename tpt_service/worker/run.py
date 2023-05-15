import logging
import os
from multiprocessing import Process, get_context
from tpt_service.worker.tpt_worker import TPTWorker


## WORKER INITIALIZATION ##
if __name__ == '__main__':
    if int(os.getenv('MAX_THREADS', 4)) > 0:
        max_threads = int(os.getenv('MAX_THREADS', 4))

    debug = False
    if int(os.getenv('DEBUG', 1)):
        debug = True

    logger = logging.getLogger("tpt_worker")
    logger.setLevel(logging.INFO)
    if debug is True:
        logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    if debug is True:
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_format)
    logger.addHandler(ch)

    logger.info("TPT Workers starting")
    # To avoid conflicts, only one request is processed, but if there are multiple threads,
    # requests preparation is performed in parallel
    tpt_worker = TPTWorker(tasks=['extract', 'analyze', 'compare', 'update'], logger=logger)
    p = Process(target=tpt_worker.run, args=(0,))
    p.start()  # starts new worker thread
    logger.info("TPT main worker started")

    if max_threads >= 1:
        logger.info("TPT will start {} addicional workers". format(max_threads))
        idx = 1

        with get_context("spawn").Pool(max_threads) as pool:
            tpt_worker = TPTWorker(tasks=['compare'], logger=logger)
            args = []
            for i in range(1, max_threads+1):
                args.append(i)
            try:
                pool.map(tpt_worker.run, args)
                pool.close()
            except Exception:
                pool.terminate()

    p.join()
