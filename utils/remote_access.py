import subprocess
import time
import json
import os

class RemoteAccessManager:
    def __init__(self):
        self.ngrok_process = None
        self.public_url = None
        self.ngrok_path = os.path.join(os.path.dirname(__file__), '../ngrok')
        self.authtoken = None
        self.last_error = None
        
        config_path = os.path.join(os.path.dirname(__file__), '../config/ngrok_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.authtoken = config.get('authtoken')
                    if self.authtoken and 'http' in self.authtoken:
                        self.authtoken = None
                        print("⚠️ 检测到无效的ngrok token配置，已清除")
            except:
                pass
    
    def set_authtoken(self, authtoken):
        if not authtoken or 'http' in authtoken.lower():
            self.last_error = '请输入有效的ngrok认证token，不要输入URL'
            return False
        
        self.authtoken = authtoken
        config_path = os.path.join(os.path.dirname(__file__), '../config/ngrok_config.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump({'authtoken': authtoken}, f)
        
        result = subprocess.run([self.ngrok_path, 'config', 'add-authtoken', authtoken],
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            self.last_error = f'ngrok配置失败: {result.stderr}'
            return False
        
        print("✅ ngrok认证已配置")
        return True
    
    def start_ngrok(self, port=8080):
        if self.ngrok_process and self.ngrok_process.poll() is None:
            return self.public_url
        
        if not self.authtoken:
            self.last_error = '请先配置ngrok认证token'
            return None
        
        try:
            env = os.environ.copy()
            env['NGROK_AUTHTOKEN'] = self.authtoken
            
            self.ngrok_process = subprocess.Popen(
                [self.ngrok_path, 'http', str(port), '--log=stdout'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )
            
            time.sleep(5)
            
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:4040/api/tunnels'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    tunnels = data.get('tunnels', [])
                    if tunnels:
                        self.public_url = tunnels[0]['public_url']
                        print(f"✅ ngrok 公网地址: {self.public_url}")
                        self.last_error = None
                        return self.public_url
                except Exception as e:
                    self.last_error = f'解析ngrok响应失败: {e}'
            
            if self.ngrok_process.poll() is not None:
                stdout, _ = self.ngrok_process.communicate()
                self.last_error = f'ngrok进程异常退出: {stdout[-200:] if len(stdout) > 200 else stdout}'
            else:
                self.last_error = 'ngrok启动成功但未获取到公网地址，请检查网络连接'
            
            print(f"⚠️ ngrok错误: {self.last_error}")
            return None
            
        except Exception as e:
            self.last_error = f'ngrok启动失败: {e}'
            print(f"⚠️ ngrok启动失败: {e}")
            return None
    
    def stop_ngrok(self):
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process.wait()
            self.ngrok_process = None
            self.public_url = None
            print("✅ ngrok已停止")
    
    def get_public_url(self):
        if not self.public_url:
            self.start_ngrok()
        return self.public_url
    
    def is_running(self):
        return self.ngrok_process is not None and self.ngrok_process.poll() is None
    
    def get_status(self):
        return {
            'running': self.is_running(),
            'public_url': self.public_url,
            'authtoken_configured': self.authtoken is not None,
            'last_error': self.last_error
        }

remote_access = RemoteAccessManager()