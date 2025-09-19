from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
import os, sqlite3, time

# Xử lý đọc file input.inp và tạo thông báo
def tao_thong_bao(path):
    if not os.path.exists(path):
        return ("Không tìm thấy file", "")
    with open(path, encoding='utf-8') as fi:
        lop_10 = {"Đúng giờ": [], "Muộn giờ": [], "Không có": []}
        lop_11 = {"Đúng giờ": [], "Muộn giờ": [], "Không có": []}
        n = int(fi.readline())
        for i in range(n):
            lop, dg = fi.readline().strip().split('-')
            lop_10[dg].append(lop)
        n = int(fi.readline())
        for i in range(n):
            lop, dg = fi.readline().strip().split('-')
            lop_11[dg].append(lop)
    for d in [lop_10, lop_11]:
        for k in d:
            d[k].sort()
    ngay_trong_tuan = ['thứ hai','thứ ba','thứ tư','thứ năm','thứ sáu','thứ bảy','chủ nhật']
    thgian = datetime.now()
    k10 = f"Thông báo kiểm tra điểm danh Khối 10 lúc {thgian.strftime('%X')}, {ngay_trong_tuan[int(thgian.strftime('%w'))-1]} ngày {thgian.strftime('%d/%m/%Y')}\n"
    k10 += f"- Đúng giờ: {', '.join(lop_10['Đúng giờ']) or 'Không có'}\n"
    k10 += f"- Muộn giờ: {', '.join(lop_10['Muộn giờ']) or 'Không có'}\n"
    k10 += f"- Không có: {', '.join(lop_10['Không có']) or 'Không có'}"
    k11 = f"Thông báo kiểm tra điểm danh Khối 11 lúc {thgian.strftime('%X')}, {ngay_trong_tuan[int(thgian.strftime('%w'))-1]} ngày {thgian.strftime('%d/%m/%Y')}\n"
    k11 += f"- Đúng giờ: {', '.join(lop_11['Đúng giờ']) or 'Không có'}\n"
    k11 += f"- Muộn giờ: {', '.join(lop_11['Muộn giờ']) or 'Không có'}\n"
    k11 += f"- Không có: {', '.join(lop_11['Không có']) or 'Không có'}"
    return k10, k11

# DB Lịch sử
DB = 'history.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT, k10 TEXT, k11 TEXT)''')
conn.commit()
conn.close()

class MainScreen(Screen):
    k10 = StringProperty()
    k11 = StringProperty()
    history = ListProperty()
    input_path = StringProperty('input.inp')

    def on_pre_enter(self):
        self.update_data()
        Clock.schedule_interval(lambda dt: self.update_data(), 2)
        self.load_history()

    def update_data(self):
        if os.path.exists(self.input_path):
            k10,k11 = tao_thong_bao(self.input_path)
            if k10!=self.k10 or k11!=self.k11:
                self.k10,self.k11 = k10,k11
                self.save_history(k10,k11)

    def copy_to_clipboard(self, text):
        Clipboard.copy(text)
        Snackbar(text="Đã copy vào clipboard").open()

    def share(self, text):
        if platform=='android':
            from jnius import autoclass, cast
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('text/plain')
            intent.putExtra(Intent.EXTRA_TEXT, cast('java.lang.CharSequence', String(text)))
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(Intent.createChooser(intent, String('Chia sẻ qua')))
        else:
            Snackbar(text="Tính năng chia sẻ chỉ hỗ trợ trên Android").open()

    def save_history(self,k10,k11):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO history(time,k10,k11) VALUES (?,?,?)",(datetime.now().isoformat(),k10,k11))
        conn.commit(); conn.close()
        self.load_history()

    def load_history(self):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT id,time FROM history ORDER BY id DESC")
        self.history = c.fetchall()
        conn.close()

    def show_history(self, hid):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT k10,k11 FROM history WHERE id=?",(hid,))
        row = c.fetchone()
        conn.close()
        if row:
            self.k10,self.k11 = row
            Snackbar(text=f"Đã tải lịch sử #{hid}").open()

class Root(ScreenManager):
    pass

class KhoiDiemDanhApp(MDApp):
    def build(self):
        self.title = "Điểm danh"
        return Root()

if __name__=='__main__':
    KhoiDiemDanhApp().run()
