import asyncio

from travertino.size import at_least

from toga_iOS.libs import CGSize, UIProgressView, UIProgressViewStyle
from toga_iOS.widgets.base import Widget

# Implementation notes
# ====================
#
# * UIProgressView doesn't have any concept of running; we track the running
#   status for API compliance.
#
# * UIProgressView doesn't have any concept of an indeterminate progress bar. A
#   background task animating between 95% and 5% is used to represent
#   indeterminate progress.
#
# * UIProgressView uses 0-1 floating point range. We track the Toga max value
#   internally for scaling purposes.


async def indeterminate_animator(progressbar):
    """A workaround for the lack of an indeterminate progressbar.

    A background task that animates between a value of 0.95 and 0.05
    on a 1 second period.
    """
    value = 0.95
    while True:
        progressbar.native.setProgress(value, animated=True)
        value = 1 - value
        await asyncio.sleep(1.0)


class ProgressBar(Widget):
    def create(self):
        self.native = UIProgressView.alloc().initWithProgressViewStyle_(
            UIProgressViewStyle.Default
        )
        self.add_constraints()

        self._running = False
        self._task = None
        self._max = 1.0

    def is_running(self):
        return self._running

    def _start_indeterminate(self):
        # Fake indeterminate progress
        self._task = asyncio.create_task(indeterminate_animator(self))

    def _stop_indeterminate(self):
        if self._task:
            self._task.cancel()
        self.native.setProgress(0.0, animated=False)

    def start(self):
        self._running = True
        if self._max is None:
            self._start_indeterminate()

    def stop(self):
        self._running = False
        if self._max is None:
            self._stop_indeterminate()

    def get_value(self):
        if self._max is None:
            return None

        return self.native.progress * self._max

    def set_value(self, value):
        if self._max is not None:
            self.native.setProgress(
                value / self._max,
                animated=True,
            )

    def get_max(self):
        return self._max

    def set_max(self, value):
        self._max = value
        if self._max is None:
            if self._running:
                self._start_indeterminate()
            else:
                self._stop_indeterminate()
        else:
            self._stop_indeterminate()

    def rehint(self):
        fitting_size = self.native.systemLayoutSizeFittingSize(CGSize(0, 0))
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = fitting_size.height
