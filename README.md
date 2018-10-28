## iOS 自动打包

- Fastlane
- Jenkins
- Python
- Ruby
- Shell

xcodebuild “最后的劳动者”

## 概念

workspace(.xcworkspace)可包含多个 projet，并管理它们的相互引用；

project(.xcodeproj) 可包含多个 targets，是代码文件、资源、配置信息的仓库；

targets 配置，给编译系统提供输入（编译那几个文件，使用什么编译脚本）

scheme 配置 targets 使用什么 build configuration 与 executable configuration。[Build, Run, Test, Profile, Analyze, Archive]编译，运行，单元测试，动态分析，静态代码分析以及打包


## python 3
1、将 autobuild.py 、exportOptions.plist文件放到你的项目根目录下（即与xx.xcworkspace或者xx.xcworkspace在同一个目录下）  
2、修改配置：autobuild.py
3、运行脚本：autobuild.py
如果你是xx.xcodeproj  `./autobuild.py -p youproject.xcodeproj`  

如果你是xx.xcworkspace`./autobuild.py -w youproject.xcworkspace`  

4、最终会在桌面生成带有时间戳的文件夹，含义ipa以及xcarchive文件
5、endmail.py是发邮件脚本，若要打包发布成功后发送邮件通知某人，请在autobuild.py里引入该模块，调用即可。
