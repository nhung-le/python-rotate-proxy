import random
from datetime import datetime
import zipfile
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

proxy_user = "proxyuser"
range = 100
proxy_hosts = [
                    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
                    "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
                    "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15",
                   ]
proxy_pass = "yourpassword" # password
proxy_port = 1001 # port

last = now = 0

# Start display first before get url
display = Display(visible=0, size=(800, 600))
display.start()

for page in range(range):
        # ROTATE PROXIES MANUALLY
    while (now == last):
        now = random.randint(0, len(proxy_hosts) -1)
    last = now
    proxy_host = proxy_hosts[now]
    proxy_url = proxy_user + ":" + proxy_pass + "@" + proxy_host + ":" + str(proxy_port)

    url = "https://ipv4.icanhazip.com"
    driver = ""

    try:
        manifest_json = """
                    {
                        "version": "1.0.0",
                        "manifest_version": 2,
                        "name": "Chrome Proxy",
                        "permissions": [
                            "proxy",
                            "tabs",
                            "unlimitedStorage",
                            "storage",
                            "<all_urls>",
                            "webRequest",
                            "webRequestBlocking"
                        ],
                        "background": {
                            "scripts": ["background.js"]
                        },
                        "minimum_chrome_version":"22.0.0"
                    }
                    """
        background_js = """
                    var config = {
                            mode: "fixed_servers",
                            rules: {
                            singleProxy: {
                                scheme: "http",
                                host: "%s",
                                port: parseInt(%s)
                            },
                            bypassList: ["localhost"]
                            }
                        };

                    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                    function callbackFn(details) {
                        return {
                            authCredentials: {
                                username: "%s",
                                password: "%s"
                            }
                        };
                    }

                    chrome.webRequest.onAuthRequired.addListener(
                                callbackFn,
                                {urls: ["<all_urls>"]},
                                ['blocking']
                    );
                    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)

        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server=%s' % proxy_url)
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage")
        #options.add_argument("--start-maximized")
        #options.add_argument('window-size=2560,1440')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-gpu')

        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)

        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.get(url)

        # SCREENSHOT TO CHECK IP CHANGED DYNAMICALLY DEPEND ON YOUR PROXY
        driver.save_screenshot(str(page) + 'image.png')

        driver.close()
        driver.quit()
    except TimeoutException as e:
        print(str(e))
        driver.close()
        driver.quit()
    except Exception as e:
        print(str(e))
        driver.close()
        driver.quit()

display.stop()
