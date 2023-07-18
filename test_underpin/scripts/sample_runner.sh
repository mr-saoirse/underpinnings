#bin/bash
#for the reference app we can run underin from anywhere and point to where the source dir is and expect a full run
underpin /
  --source-dir $1 /
  --job '{}'
  --source-repo git@github.com:mr-saoirse/underpinnings.git /
  --target-repo git@github.com:mr-saoirse/cloud-stack.git
