module.exports = {
    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = "Mortality Monitor";
                return args;
            })
    },
    runtimeCompiler: true,
}