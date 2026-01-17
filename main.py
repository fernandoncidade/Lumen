from source.utils.LogManager import LogManager
from source.src_01_SplashAppStarter import SplashAppStarter

LogManager.enable_startup_diagnostics()
LogManager.install_exception_hook()

if __name__ == '__main__':
    SplashAppStarter().start()
