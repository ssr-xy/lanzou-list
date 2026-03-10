import sys
import json
import time
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapling_framework'))

from scrapling.fetchers import StealthySession

class LanZouCloud:
    def __init__(self, ylogin, phpdisk_info):
        self.ylogin = ylogin
        self.phpdisk_info = phpdisk_info
        self.cookies = [
            {'name': 'ylogin', 'value': ylogin, 'domain': '.woozooo.com', 'path': '/'},
            {'name': 'phpdisk_info', 'value': phpdisk_info, 'domain': '.woozooo.com', 'path': '/'}
        ]
        self.all_files = []
        self.user_data_dir = os.path.join(os.path.dirname(__file__), 'browser_data')
        
    def make_post_request(self, page, task, folder_id=-1, file_id=None):
        if file_id:
            body = f'task={task}&file_id={file_id}'
        else:
            body = f'task={task}&folder_id={folder_id}'
        
        js_code = f'''
        async () => {{
            const response = await fetch('https://up.woozooo.com/doupload.php', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                }},
                body: '{body}'
            }});
            return await response.text();
        }}
        '''
        result = page.evaluate(js_code)
        try:
            return json.loads(result)
        except:
            return None
    
    def get_share_link(self, page, file_id):
        result = self.make_post_request(page, 22, file_id=file_id)
        if result and result.get('zt') == 1:
            info = result.get('info', {})
            f_id = info.get('f_id', '')
            pwd = info.get('pwd', '')
            return f_id, pwd
        return None, None
    
    def get_files_from_dom(self, page):
        js_code = '''
        () => {
            const files = [];
            const spans = document.querySelectorAll('span[id^="filename"]');
            spans.forEach(span => {
                const idMatch = span.id.match(/filename(\\d+)/);
                if (idMatch) {
                    const fileId = idMatch[1];
                    const name = span.textContent.trim();
                    files.push({id: fileId, name: name});
                }
            });
            return files;
        }
        '''
        return page.evaluate(js_code)
    
    def get_folders_from_dom(self, page):
        js_code = '''
        () => {
            const folders = [];
            const items = document.querySelectorAll('.f_tb[id^="fol"]');
            items.forEach(item => {
                const idMatch = item.id.match(/fol(\\d+)/);
                if (idMatch) {
                    const folderId = idMatch[1];
                    const nameSpan = item.querySelector('[id^="folname"]');
                    const folderName = nameSpan ? nameSpan.textContent.trim() : '';
                    folders.push({
                        folder_id: folderId,
                        folder_name: folderName
                    });
                }
            });
            return folders;
        }
        '''
        return page.evaluate(js_code)
    
    def load_all_files(self, page):
        print("  加载所有文件...")
        max_attempts = 50
        attempt = 0
        
        while attempt < max_attempts:
            is_hidden = page.evaluate('''
                () => {
                    const el = document.getElementById('filemore');
                    if (!el) return true;
                    const style = el.getAttribute('style') || '';
                    return style.includes('display: none') || style.includes('display:none');
                }
            ''')
            if is_hidden:
                break
            
            more_btn = page.query_selector('#filemore .btn')
            if more_btn:
                more_btn.click()
                time.sleep(1)
                page.wait_for_load_state('networkidle')
            else:
                break
            
            attempt += 1
        
        return attempt
    
    def process_folder(self, page, folder_id=-1, folder_path=""):
        url = f'https://up.woozooo.com/mydisk.php?item=files&action=index&folder_id={folder_id}'
        print(f"\n访问: {url}")
        
        page.goto(url)
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        
        self.load_all_files(page)
        
        files = self.get_files_from_dom(page)
        print(f"找到 {len(files)} 个文件")
        
        for f in files:
            file_id = f.get('id')
            file_name = f.get('name', '未知')
            
            f_id, pwd = self.get_share_link(page, file_id)
            if f_id:
                share_url = f"https://www.lanzoui.com/{f_id}"
                self.all_files.append({
                    'name': file_name,
                    'path': folder_path,
                    'share_url': share_url,
                    'password': pwd
                })
                print(f"  ✓ {file_name[:40]}...")
            time.sleep(0.15)
        
        folders = self.get_folders_from_dom(page)
        if folders:
            print(f"发现 {len(folders)} 个子文件夹")
            for folder in folders:
                sub_folder_id = folder.get('folder_id')
                sub_folder_name = folder.get('folder_name', '')
                new_path = f"{folder_path}/{sub_folder_name}" if folder_path else sub_folder_name
                
                print(f"\n[文件夹] {sub_folder_name}")
                self.process_folder(page, sub_folder_id, new_path)
    
    def get_all_shares(self):
        print("使用持久化浏览器会话...")
        print("=" * 60)
        
        def page_action(page):
            print(f"页面标题: {page.title()}")
            
            print("\n等待页面完全加载...")
            time.sleep(3)
            page.wait_for_load_state('networkidle')
            
            print("\n开始扫描文件和文件夹...")
            print("[根目录]")
            self.process_folder(page, -1, "")
            
            return None
        
        with StealthySession(
            headless=True,
            network_idle=True,
            cookies=self.cookies,
            google_search=False,
            user_data_dir=self.user_data_dir,
            wait=2000,
            hide_canvas=True
        ) as session:
            session.fetch(
                'https://up.woozooo.com/mydisk.php?item=files&action=index',
                wait_selector='body',
                page_action=page_action
            )
        
        print("=" * 60)
        return self.all_files


def main():
    ylogin = 'YOUR_YLOGIN_HERE'
    phpdisk_info = 'YOUR_PHPDISK_INFO_HERE'
    
    if ylogin == 'YOUR_YLOGIN_HERE':
        print("请先在脚本中设置你的蓝奏云凭证 (ylogin 和 phpdisk_info)")
        print("\n获取方法:")
        print("1. 登录蓝奏云: https://up.woozooo.com/")
        print("2. 按 F12 打开开发者工具")
        print("3. 切换到 Application (应用程序) 标签")
        print("4. 在左侧找到 Cookies -> https://up.woozooo.com")
        print("5. 复制 ylogin 和 phpdisk_info 的值")
        return
    
    lz = LanZouCloud(ylogin, phpdisk_info)
    files = lz.get_all_shares()
    
    print(f"\n\n总共找到 {len(files)} 个文件的分享链接:")
    print("=" * 60)
    
    current_path = ""
    for f in files:
        if f['path'] != current_path:
            current_path = f['path']
            print(f"\n[{current_path if current_path else '根目录'}]")
        print(f"  {f['name'][:40]}")
        print(f"  链接: {f['share_url']}" + (f" 密码: {f['password']}" if f['password'] else ""))
    
    output_file = os.path.join(os.path.dirname(__file__), 'lanzou_shares.txt')
    with open(output_file, 'w', encoding='utf-8') as out:
        for f in files:
            line = f"{f['path']}\t{f['name']}\t{f['share_url']}"
            if f['password']:
                line += f"\t密码: {f['password']}"
            out.write(line + '\n')
    print(f"\n结果已保存到 {output_file}")


if __name__ == '__main__':
    main()
