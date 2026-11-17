from PySide6.QtCore import QObject, QRunnable, Signal, QThreadPool


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
            try:
                self.signals.result.emit(res)
            except RuntimeError:
                pass
        except Exception as exc:
            msg = str(exc)
            if hasattr(exc, "message") and exc.message:
                msg = exc.message
            try:
                self.signals.error.emit(msg)
            except RuntimeError:
                pass
        finally:
            try:
                self.signals.finished.emit()
            except RuntimeError:
                pass


_active_workers = set()


def run_in_background(
    fn,
    *args,
    on_success=None,
    on_error=None,
    on_finished=None,
    **kwargs,
) -> Worker:
    worker = Worker(fn, *args, **kwargs)
    _active_workers.add(worker)

    if on_success:
        worker.signals.result.connect(on_success)
    if on_error:
        worker.signals.error.connect(on_error)

    def _cleanup():
        _active_workers.discard(worker)
        if on_finished:
            on_finished()

    worker.signals.finished.connect(_cleanup)
    QThreadPool.globalInstance().start(worker)
    return worker
