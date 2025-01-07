#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo -e "${YELLOW}请选择操作:${NC}"
    echo "1. 编译项目"
    echo "2. 运行项目"
    echo "3. 清理并重新编译"
    echo "4. 编译并运行"
    echo "0. 退出"
}

# 编译项目
compile() {
    echo -e "${GREEN}正在编译项目...${NC}"
    mvn compile
}

# 运行项目
run() {
    echo -e "${GREEN}正在运行项目...${NC}"
    java -jar target/api-test-1.0-SNAPSHOT-jar-with-dependencies.jar
}

# 清理并重新编译
clean_compile() {
    echo -e "${GREEN}正在清理并重新编译项目...${NC}"
    mvn clean package
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-4): " choice
    
    case $choice in
        1)
            compile
            ;;
        2)
            if [ ! -f "target/api-test-1.0-SNAPSHOT-jar-with-dependencies.jar" ]; then
                echo -e "${YELLOW}JAR文件不存在，需要先编译项目${NC}"
                compile
            fi
            run
            ;;
        3)
            clean_compile
            ;;
        4)
            clean_compile
            run
            ;;
        0)
            echo -e "${GREEN}退出程序${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}无效选项，请重新选择${NC}"
            ;;
    esac
    
    echo
done
