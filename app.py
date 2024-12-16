from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# 设置上传文件夹路径
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'xls'}  # 允许上传的文件类型

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 判断文件扩展名是否符合要求
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 假设你已经有一个分析函数
def analyze_file(file_path):
    # 这里填入你的分析代码
    # 返回一个分析结果，示例：
    import pandas as pd  # 导入库
    df = pd.read_excel(file_path)  # 读取数据
    total_production = df["重量"].sum()  # 总重量
    # 查询汽车外板相关数据
    # 最终用途的第三位若为1，则是汽车外板
    automobile_outer_panel_df = df[df["最终用途"].str[2] == '1']  # 查询汽车外板数据
    automobile_outer_panel_production = automobile_outer_panel_df["重量"].sum()  # 汽车外板产量
    # 查询高强钢相关数据
    # 出钢记号的第三位若大于等于5，则判定为高强钢
    high_strength_steel_df = df[df["出钢记号"].str[2].astype(int) >= 4]  # 查询高强钢相应数据
    high_strength_steel_production = high_strength_steel_df['重量'].sum()  # 高强钢产量
    # 查询普料相关数据
    # 除去汽车外板外的所有数据
    outer_panel_df_remaining = df[~df.isin(automobile_outer_panel_df.to_dict(orient='list')).all(axis=1)]
    # 在此基础上除去高强钢的数据即为普料数据
    ordinary_material = outer_panel_df_remaining[
        ~outer_panel_df_remaining.isin(high_strength_steel_df.to_dict(orient='list')).all(axis=1)]
    ordinary_material_production = ordinary_material["重量"].sum()  # 普料产量
    ordinary_material_thickness_lower_1_production = ordinary_material[ordinary_material['出口材料厚度平均'] < 1.0][
        "重量"].sum()  # 普料厚度小于1.0mm的产量
    analyze_result=[f"总产量{total_production / 1000}吨",f"汽车外板{automobile_outer_panel_production / 1000}吨",f"高强钢{high_strength_steel_production / 1000}吨",
                    f"普料{ordinary_material_production / 1000}吨",f"普料厚度＜1.0mm共计{ordinary_material_thickness_lower_1_production / 1000}吨"]
    print(f"总产量{total_production / 1000}吨")
    print(f"汽车外板{automobile_outer_panel_production / 1000}吨")
    print(f"高强钢{high_strength_steel_production / 1000}吨")
    print(f"普料{ordinary_material_production / 1000}吨")
    print(f"普料厚度＜1.0mm共计{ordinary_material_thickness_lower_1_production / 1000}吨")
    return analyze_result


@app.route('/')
def index():
    return render_template('upload.html')


# 文件上传接口
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # 保存上传的文件
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 调用分析函数
        result = analyze_file(filepath)

        return render_template('upload.html', result=result)

    return "不允许的文件类型！"


if __name__ == '__main__':
    # 创建上传目录
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(host='0.0.0.0', port=5000)

