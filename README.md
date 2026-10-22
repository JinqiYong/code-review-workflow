#AI代码自修复Agent工作流

1.用户提交任务，编码Agent生成初始代码，代码存入共享状态current_code
2.审查Agent调用检查工具对代码进行校验
3.审查通过（PASS）：流程结束
4.审查失败（FAIL）：交给修复Agent根据报错信息修改代码，更新current_code，再次回到审查Agent进行校验，循环迭代直到审查通过