def ignite_version = readFileFromWorkspace('ignite_version.txt')

folder(ignite_version) {
    displayName('Release ' + ignite_version)
    description('Distributed tests for release ' + ignite_version)

    job('prepare') {
        parameters {
            string(name='IGNITE_VERSION', defaultValue=ignite_version)
        }
        steps {
             shell('set')
        }
    }
}