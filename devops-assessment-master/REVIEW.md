## 1. Where is the code?
The app folder is practically empty. Everything downstream depends on a working service.

## 2. Helm references are off

Service selector is "app: myapps" but pods are labelled "myapp", the Service matches no pods.
Ingress backend points to "homeworks", which is not the Service name.
Container port is 5000, while in the task the service port must be 8080.

## 3. Missing Templating
Names are hardcoded to myapp and replicaCount from values are ignored. Template the
manifests, add probes on /health, and set sensible resources — this is what makes
the deployment reliable and self-healing.

## 4. The CI pipeline does nothing
The whole CI pipeline is a placeholder, it requires AT LEAST a linting stage for ALL POSSIBLE CODES.
Also include a stage that runs unit tests and a deploy stage to the environments.
(Author's note: In this stage of a ticket, there already should be a preexisting CI pipeline)

## 5. Clean Git
Upon opening a ticket always pull from the latest corresponding branch (eg. last commit of Main).
Name the branch with a telling name either don't spam the branch with commits like "wip", "coding" or squash before MR posting.


