def jobFolder = "User_tests/mshonichev"
def jobName = "${jobFolder}/test-pipe-from-seed"
def branchName = "master"

jobDsl(jobName) {

    parameters(
        string(defaultValue: '2.5.1-p8', description: 'Ignite version', name: 'IGNITE_VERSION'),
        string(defaultValue: '8.5.1-p8', description: 'GridGain version', name: 'GRIDGAIN_VERSION'),
    )
    scm {
        git("git://github.com/tiden.git", branchName)
    }
    steps {
        sh '''
            bash -x utils/prepare_work_directory.sh
        '''
    }
}
