import fcntl
import os


def lock_path(display):
    return '/tmp/.X%d-lock' % display


def get_lock(display):
    lockfile = lock_path(display)
    try:
        with open(lockfile, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True  # successfully got a lock
    except OSError:
        return False  # failed to get a lock


def release_lock(display):
    lockfile = lock_path(display)
    try:
        with open(lockfile, "r") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        os.remove(lockfile)
    except FileNotFoundError:
        pass


def find_display():
    display = 10
    while True:
        if get_lock(display):
            return display
        display += 1



class Fixture1:
    def __enter__(self):
        self._old_display = os.environ.get("DISPLAY")
        os.environ["DISPLAY"] = ":%d" % self._find_display()
        return self

    def __exit__(self, type, value, traceback):
        try:
            release_lock(self._display)
        except OSError as e:
            pass

        if self._old_display is None:
            del os.environ["DISPLAY"]
        else:
            os.environ["DISPLAY"] = self._old_display

    def _find_display(self):
        if hasattr(self, '_display'):
            return self._display
        self._display = find_display()
        return self._display

class Fixture2:
    def __enter__(self):
        self.display = os.environ["DISPLAY"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture(scope="session")
def fixture1():
    with Fixture1():
        yield


@pytest.fixture(scope="function")
def fixture2(request, fixture1):
    with Fixture2() as x:
        yield x
