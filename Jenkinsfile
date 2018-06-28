def jobFolder = "User_tests/mshonichev"
def jobName = "${jobFolder}/test-pipe-from-seed"
def branchName = "master"

def jobDSL="""
node {
  stage("test"){
   echo 'Hello World'
  }
}

""";
//http://javadoc.jenkins.io/plugin/workflow-cps/index.html?org/jenkinsci/plugins/workflow/cps/CpsFlowDefinition.html
def flowDefinition = new org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition(jobDSL, true);
//http://javadoc.jenkins.io/jenkins/model/Jenkins.html
def parent = Jenkins.instance;
//parent=Jenkins.instance.getItemByFullName("parentFolder/subFolder")
//http://javadoc.jenkins.io/plugin/workflow-job/org/jenkinsci/plugins/workflow/job/WorkflowJob.html
def job = new org.jenkinsci.plugins.workflow.job.WorkflowJob(parent, "testJob")
job.definition = flowDefinition

job.setConcurrentBuild(false);

//http://javadoc.jenkins.io/plugin/branch-api/jenkins/branch/RateLimitBranchProperty.html
job.addProperty( new jenkins.branch.RateLimitBranchProperty.JobPropertyImpl
    (new jenkins.branch.RateLimitBranchProperty.Throttle (60,"hours")));
def spec = "H 0 1 * *";
hudson.triggers.TimerTrigger newCron = new hudson.triggers.TimerTrigger(spec);
newCron.start(job, true);
job.addTrigger(newCron);
job.save();


Jenkins.instance.reload()
