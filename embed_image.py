import base64
import os
import sys

def convert_image_to_base64(image_path, output_readme_path):
    if not os.path.exists(image_path):
        print(f"❌ 错误: 找不到图片文件 '{image_path}'")
        return False
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    base64_str = base64.b64encode(image_data).decode('utf-8')
    
    print(f"✅ 图片信息:")
    print(f"   文件大小: {len(image_data) / 1024:.1f} KB")
    print(f"   Base64长度: {len(base64_str)} 字符")
    
    markdown_image = f'data:image/png;base64,{base64_str}'
    
    with open(output_readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_pattern = '![爆红追踪界面](https://raw.githubusercontent.com/chanzsam/HotTrack/main/screenshots/viral-tracking.png)'
    new_content = content.replace(old_pattern, f'![爆红追踪界面]({markdown_image})')
    
    with open(output_readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ 成功! 图片已内嵌到 README.md")
    print(f"   📝 文件: {output_readme_path}")
    print(f"   🔒 状态: Base64编码，永久有效!")
    return True

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(base_dir, 'screenshots', 'viral-tracking.png')
    readme_path = os.path.join(base_dir, 'README.md')
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    print("=" * 50)
    print("🖼️  HotTrack 图片嵌入工具")
    print("=" * 50)
    print(f"\n📂 图片路径: {image_path}")
    print(f"📄 README:   {readme_path}\n")
    
    success = convert_image_to_base64(image_path, readme_path)
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 下一步: git add . && git commit && git push")
        print("=" * 50)
    else:
        print("\n💡 请先将截图保存到: screenshots/viral-tracking.png")
        sys.exit(1)
