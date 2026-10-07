# 语言规则如何具体化

从源码、语言清单、锁文件、构建/格式/静态检查/测试配置确认真实语言、版本与工具。使用 [语言规则模板](../assets/templates/language-standard.md)，每个适用主题写直接规则、项目短例与真实检查；不把“使用最佳实践”当规则。不默认引入新框架、工具或覆盖率阈值。

## Go 项目

以 `go.mod` 的 go/toolchain 声明与 CI 配置分别记录最低/选用工具链，运行版本单列。命名沿用包现状；检查错误，使用 `%w` 保留错误链，调用方用 `errors.Is/As` 判断；跨边界传递 `context.Context`，说明取消与超时归属。资源获取成功后按生命周期释放，goroutine 必须有退出与等待方案。接口在消费方/项目约定位置定义，不能为每个结构体机械创建接口。格式与检查采用仓库已有命令。

教学函数片段（需放入有 fmt 导入的 package；实际错误语义由项目约定）：

```go
func loadOrder(id string, load func(string) error) error {
    if err := load(id); err != nil {
        return fmt.Errorf("load order %s: %w", id, err)
    }
    return nil
}
```

参考：[Go module reference](https://go.dev/ref/mod)、[错误包装](https://go.dev/blog/go1.13-errors)、[context 文档](https://pkg.go.dev/context)。生成时核实项目支持的版本；片段不是完整应用。

## Java 项目

以 Maven/Gradle toolchain/release 配置与 CI 确认编译目标和运行时，不凭本机 JDK 推断。命名、package、异常与事务遵守项目约定；异常保留 cause，协议层负责映射，禁止吞异常或记录后无差别成功返回。可关闭资源使用 try-with-resources；明确线程/异步任务生命周期与事务边界，不能假设注解跨自调用或线程仍有效。框架和空值规则从实际项目选择，不默认 Spring 或特定注解库。

教学函数片段（需有 java.nio.file/java.io 导入；UTF-8 来自该 API 的约定）：

```java
static String firstLine(Path path) throws IOException {
    try (BufferedReader reader = Files.newBufferedReader(path)) {
        return reader.readLine();
    }
}
```

参考：[Java try-with-resources](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)、[Files API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html)。只采用真实编译目标支持的 API。

其他语言同样绑定项目配置与官方资料。每种语言规则与前端、数据库、测试规则各司其职，入口的目录归属始终权威。
