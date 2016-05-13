permissionSet = [
    # "apikey:access",
    "nexus:*",
    # "nexus:analytics",
    # "nexus:artifact",
    # "nexus:atlas",
    # "nexus:attributes",
    # "nexus:authentication",
    # "nexus:browseremote",
    "nexus:cache",
    # "nexus:capabilities",
    # "nexus:capabilityTypes",
    # "nexus:command",
    # "nexus:componentrealmtypes",
    # "nexus:componentscheduletypes",
    # "nexus:componentscontentclasses",
    # "nexus:componentsrepotypes",
    "nexus:configuration",
    # "nexus:feeds",
    # "nexus:healthcheck",
    # "nexus:healthchecksummary",
    # "nexus:identify",
    # "nexus:index",
    "nexus:ldapconninfo",
    "nexus:ldaptestauth",
    "nexus:ldaptestuserconf",
    "nexus:ldapusergroupconf",
    "nexus:ldapuserrolemap",
    # "nexus:logconfig",
    "nexus:logs",
    # "nexus:metadata",
    # "nexus:metrics-endpoints",
    # "nexus:pluginconsoleplugininfos",
    "nexus:repogroups",
    # "nexus:repometa",
    "nexus:repositories",
    # "nexus:repositorymirrors",
    # "nexus:repositorymirrorsstatus",
    # "nexus:repositorypredefinedmirrors",
    "nexus:repostatus",
    # "nexus:repotemplates",
    # "nexus:routes",
    "nexus:settings",
    "nexus:status",
    "nexus:targets",
    "nexus:tasks",
    "nexus:tasksrun",
    # "nexus:tasktypes",
    # "nexus:wastebasket",
    # "nexus:wonderland",
    # "nexus:yumAlias",
    # "nexus:yumVersionedRepositories",
    "security:*",
    # "security:componentsuserlocatortypes",
    "security:privileges",
    # "security:privilegetypes",
    "security:roles",
    "security:users",
    # "security:userschangepw",
    # "security:usersforgotid",
    # "security:usersforgotpw",
    "security:usersreset",
    "security:userssetpw"
]

def getBuiltinTargs():
    return {
        "1": {
            "name": "1",
            "ptype": "maven2",
            "patterns": [".*"]
        },
        "2": {
            "name": "2",
            "ptype": "maven1",
            "patterns": [".*"]
        },
        "3": {
            "name": "3",
            "ptype": "maven2",
            "patterns": ["(?!.*-sources.*).*"]
        },
        "4": {
            "name": "4",
            "ptype": "maven2",
            "patterns": [".*maven-metadata\.xml.*"]
        },
        "any": {
            "name": "any",
            "ptype": "any",
            "patterns": [".*"]
        },
        "site": {
            "name": "site",
            "ptype": "site",
            "patterns": [".*"]
        },
        "npm": {
            "name": "npm",
            "ptype": "npm",
            "patterns": [".*"]
        },
        "nuget": {
            "name": "nuget",
            "ptype": "nuget",
            "patterns": [".*"]
        },
        "rubygems": {
            "name": "rubygems",
            "ptype": "rubygems",
            "patterns": [".*"]
        }
    }

def getBuiltinPrivs(usertargs):
    targs = getBuiltinTargs()
    targs.update(usertargs)
    return {
        "All M1 Repositories": {
            "name": "All M1 Repositories",
            "target": targs["2"],
            "repo": "*"
        },
        "All M2 Repositories": {
            "name": "All M2 Repositories",
            "target": targs["1"],
            "repo": "*"
        },
        "All npm Repositories": {
            "name": "All npm Repositories",
            "target": targs["npm"],
            "repo": "*"
        },
        "All NuGet Repositories": {
            "name": "All NuGet Repositories",
            "target": targs["nuget"],
            "repo": "*"
        },
        "All Repositories": {
            "name": "All Repositories",
            "target": targs["any"],
            "repo": "*"
        },
        "All Rubygems Repositories": {
            "name": "All Rubygems Repositories",
            "target": targs["rubygems"],
            "repo": "*"
        },
        "All Site Repositories": {
            "name": "All Site Repositories",
            "target": targs["site"],
            "repo": "*"
        }
    }

def getBuiltinPrivmap(privs):
    return {
        "repository-thirdparty": {
            "id": "repository-thirdparty",
            "repo": "thirdparty",
            "type": "view"
        },
        "repository-all": {
            "id": "repository-all",
            "repo": "*",
            "type": "view"
        },
        "repository-apache-snapshots": {
            "id": "repository-apache-snapshots",
            "repo": "apache-snapshots",
            "type": "view"
        },
        "repository-central": {
            "id": "repository-central",
            "repo": "central",
            "type": "view"
        },
        "repository-central-m1": {
            "id": "repository-central-m1",
            "repo": "central-m1",
            "type": "view"
        },
        "repository-public": {
            "id": "repository-public",
            "repo": "public",
            "type": "view"
        },
        "repository-releases": {
            "id": "repository-releases",
            "repo": "releases",
            "type": "view"
        },
        "repository-snapshots": {
            "id": "repository-snapshots",
            "repo": "snapshots",
            "type": "view"
        },
        "T6": {
            "id": "T6",
            "method": "create",
            "priv": privs["All M1 Repositories"],
            "type": "target"
        },
        "T8": {
            "id": "T8",
            "method": "delete",
            "priv": privs["All M1 Repositories"],
            "type": "target"
        },
        "T2": {
            "id": "T2",
            "method": "read",
            "priv": privs["All M1 Repositories"],
            "type": "target"
        },
        "T4": {
            "id": "T4",
            "method": "update",
            "priv": privs["All M1 Repositories"],
            "type": "target"
        },
        "T5": {
            "id": "T5",
            "method": "create",
            "priv": privs["All M2 Repositories"],
            "type": "target"
        },
        "T7": {
            "id": "T7",
            "method": "delete",
            "priv": privs["All M2 Repositories"],
            "type": "target"
        },
        "T1": {
            "id": "T1",
            "method": "read",
            "priv": privs["All M2 Repositories"],
            "type": "target"
        },
        "T3": {
            "id": "T3",
            "method": "update",
            "priv": privs["All M2 Repositories"],
            "type": "target"
        },
        "npm-create": {
            "id": "npm-create",
            "method": "create",
            "priv": privs["All npm Repositories"],
            "type": "target"
        },
        "npm-delete": {
            "id": "npm-delete",
            "method": "delete",
            "priv": privs["All npm Repositories"],
            "type": "target"
        },
        "npm-read": {
            "id": "npm-read",
            "method": "read",
            "priv": privs["All npm Repositories"],
            "type": "target"
        },
        "npm-update": {
            "id": "npm-update",
            "method": "update",
            "priv": privs["All npm Repositories"],
            "type": "target"
        },
        "nuget-create": {
            "id": "nuget-create",
            "method": "create",
            "priv": privs["All NuGet Repositories"],
            "type": "target"
        },
        "nuget-delete": {
            "id": "nuget-delete",
            "method": "delete",
            "priv": privs["All NuGet Repositories"],
            "type": "target"
        },
        "nuget-read": {
            "id": "nuget-read",
            "method": "read",
            "priv": privs["All NuGet Repositories"],
            "type": "target"
        },
        "nuget-update": {
            "id": "nuget-update",
            "method": "update",
            "priv": privs["All NuGet Repositories"],
            "type": "target"
        },
        "T11": {
            "id": "T11",
            "method": "create",
            "priv": privs["All Repositories"],
            "type": "target"
        },
        "T12": {
            "id": "T12",
            "method": "delete",
            "priv": privs["All Repositories"],
            "type": "target"
        },
        "T9": {
            "id": "T9",
            "method": "read",
            "priv": privs["All Repositories"],
            "type": "target"
        },
        "T10": {
            "id": "T10",
            "method": "update",
            "priv": privs["All Repositories"],
            "type": "target"
        },
        "rubygems-create": {
            "id": "rubygems-create",
            "method": "create",
            "priv": privs["All Rubygems Repositories"],
            "type": "target"
        },
        "rubygems-delete": {
            "id": "rubygems-delete",
            "method": "delete",
            "priv": privs["All Rubygems Repositories"],
            "type": "target"
        },
        "rubygems-read": {
            "id": "rubygems-read",
            "method": "read",
            "priv": privs["All Rubygems Repositories"],
            "type": "target"
        },
        "rubygems-update": {
            "id": "rubygems-update",
            "method": "update",
            "priv": privs["All Rubygems Repositories"],
            "type": "target"
        },
        "site-create": {
            "id": "site-create",
            "method": "create",
            "priv": privs["All Site Repositories"],
            "type": "target"
        },
        "site-delete": {
            "id": "site-delete",
            "method": "delete",
            "priv": privs["All Site Repositories"],
            "type": "target"
        },
        "site-read": {
            "id": "site-read",
            "method": "read",
            "priv": privs["All Site Repositories"],
            "type": "target"
        },
        "site-update": {
            "id": "site-update",
            "method": "update",
            "priv": privs["All Site Repositories"],
            "type": "target"
        },
        "1000": {
            "id": "1000",
            "method": "*",
            "permission": "nexus:*",
            "type": "application"
        },
        "analytics-all": {
            "id": "analytics-all",
            "method": "*",
            "permission": "nexus:analytics",
            "type": "application"
        },
        "83": {
            "id": "83",
            "method": "*",
            "permission": "apikey:access",
            "type": "application"
        },
        "54": {
            "id": "54",
            "method": "read",
            "permission": "nexus:artifact",
            "type": "application"
        },
        "65": {
            "id": "65",
            "method": "create,read",
            "permission": "nexus:artifact",
            "type": "application"
        },
        "atlas-all": {
            "id": "atlas-all",
            "method": "*",
            "permission": "nexus:atlas",
            "type": "application"
        },
        "browse-remote-repo": {
            "id": "browse-remote-repo",
            "method": "read",
            "permission": "nexus:browseremote",
            "type": "application"
        },
        "capabilities-create-read": {
            "id": "capabilities-create-read",
            "method": "create,read",
            "permission": "nexus:capabilities",
            "type": "application"
        },
        "capabilities-delete-read": {
            "id": "capabilities-delete-read",
            "method": "delete,read",
            "permission": "nexus:capabilities",
            "type": "application"
        },
        "capabilities-read": {
            "id": "capabilities-read",
            "method": "read",
            "permission": "nexus:capabilities",
            "type": "application"
        },
        "capabilities-update-read": {
            "id": "capabilities-update-read",
            "method": "update,read",
            "permission": "nexus:capabilities",
            "type": "application"
        },
        "capability-types-read": {
            "id": "capability-types-read",
            "method": "read",
            "permission": "nexus:capabilityTypes",
            "type": "application"
        },
        "19": {
            "id": "19",
            "method": "read",
            "permission": "nexus:identify",
            "type": "application"
        },
        "21": {
            "id": "21",
            "method": "delete,read",
            "permission": "nexus:cache",
            "type": "application"
        },
        "43": {
            "id": "43",
            "method": "read",
            "permission": "nexus:configuration",
            "type": "application"
        },
        "nexus-healthcheck-read": {
            "id": "nexus-healthcheck-read",
            "method": "read",
            "permission": "nexus:healthcheck",
            "type": "application"
        },
        "nexus-healthcheck-update": {
            "id": "nexus-healthcheck-update",
            "method": "update",
            "permission": "nexus:healthcheck",
            "type": "application"
        },
        "nexus-healthcheck-summary-read": {
            "id": "nexus-healthcheck-summary-read",
            "method": "read",
            "permission": "nexus:healthchecksummary",
            "type": "application"
        },
        "ldap-conn-read": {
            "id": "ldap-conn-read",
            "method": "read",
            "permission": "nexus:ldapconninfo",
            "type": "application"
        },
        "ldap-conn-update": {
            "id": "ldap-conn-update",
            "method": "update",
            "permission": "nexus:ldapconninfo",
            "type": "application"
        },
        "ldap-test-auth-conf": {
            "id": "ldap-test-auth-conf",
            "method": "update",
            "permission": "nexus:ldaptestauth",
            "type": "application"
        },
        "ldap-test-user-group-conf": {
            "id": "ldap-test-user-group-conf",
            "method": "update",
            "permission": "nexus:ldaptestuserconf",
            "type": "application"
        },
        "ldap-user-group-conf-read": {
            "id": "ldap-user-group-conf-read",
            "method": "read",
            "permission": "nexus:ldapusergroupconf",
            "type": "application"
        },
        "ldap-user-group-conf-update": {
            "id": "ldap-user-group-conf-update",
            "method": "update",
            "permission": "nexus:ldapusergroupconf",
            "type": "application"
        },
        "ldap-user-role-map-create": {
            "id": "ldap-user-role-map-create",
            "method": "create",
            "permission": "nexus:ldapuserrolemap",
            "type": "application"
        },
        "ldap-user-role-map-delete": {
            "id": "ldap-user-role-map-delete",
            "method": "delete,read",
            "permission": "nexus:ldapuserrolemap",
            "type": "application"
        },
        "ldap-user-role-map-read": {
            "id": "ldap-user-role-map-read",
            "method": "read",
            "permission": "nexus:ldapuserrolemap",
            "type": "application"
        },
        "ldap-user-role-map-update": {
            "id": "ldap-user-role-map-update",
            "method": "update",
            "permission": "nexus:ldapuserrolemap",
            "type": "application"
        },
        "77": {
            "id": "77",
            "method": "read,update",
            "permission": "nexus:logconfig",
            "type": "application"
        },
        "2": {
            "id": "2",
            "method": "read",
            "permission": "nexus:authentication",
            "type": "application"
        },
        "42": {
            "id": "42",
            "method": "read",
            "permission": "nexus:logs",
            "type": "application"
        },
        "metrics-endpoints": {
            "id": "metrics-endpoints",
            "method": "*",
            "permission": "nexus:metrics-endpoints",
            "type": "application"
        },
        "66": {
            "id": "66",
            "method": "update,read",
            "permission": "nexus:command",
            "type": "application"
        },
        "plugin-infos-read": {
            "id": "plugin-infos-read",
            "method": "read",
            "permission": "nexus:pluginconsoleplugininfos",
            "type": "application"
        },
        "55": {
            "id": "55",
            "method": "read",
            "permission": "nexus:repostatus",
            "type": "application"
        },
        "73": {
            "id": "73",
            "method": "read",
            "permission": "nexus:componentrealmtypes",
            "type": "application"
        },
        "76": {
            "id": "76",
            "method": "delete,read",
            "permission": "nexus:metadata",
            "type": "application"
        },
        "20": {
            "id": "20",
            "method": "delete,read",
            "permission": "nexus:attributes",
            "type": "application"
        },
        "18": {
            "id": "18",
            "method": "delete,read",
            "permission": "nexus:index",
            "type": "application"
        },
        "5": {
            "id": "5",
            "method": "create,read",
            "permission": "nexus:repositories",
            "type": "application"
        },
        "8": {
            "id": "8",
            "method": "delete,read",
            "permission": "nexus:repositories",
            "type": "application"
        },
        "6": {
            "id": "6",
            "method": "read",
            "permission": "nexus:repositories",
            "type": "application"
        },
        "7": {
            "id": "7",
            "method": "update,read",
            "permission": "nexus:repositories",
            "type": "application"
        },
        "70": {
            "id": "70",
            "method": "read",
            "permission": "nexus:componentscontentclasses",
            "type": "application"
        },
        "13": {
            "id": "13",
            "method": "create,read",
            "permission": "nexus:repogroups",
            "type": "application"
        },
        "16": {
            "id": "16",
            "method": "delete,read",
            "permission": "nexus:repogroups",
            "type": "application"
        },
        "14": {
            "id": "14",
            "method": "read",
            "permission": "nexus:repogroups",
            "type": "application"
        },
        "15": {
            "id": "15",
            "method": "update,read",
            "permission": "nexus:repogroups",
            "type": "application"
        },
        "79": {
            "id": "79",
            "method": "create,read",
            "permission": "nexus:repositorymirrors",
            "type": "application"
        },
        "78": {
            "id": "78",
            "method": "read",
            "permission": "nexus:repositorymirrors",
            "type": "application"
        },
        "82": {
            "id": "82",
            "method": "read",
            "permission": "nexus:repositorymirrorsstatus",
            "type": "application"
        },
        "81": {
            "id": "81",
            "method": "read",
            "permission": "nexus:repositorypredefinedmirrors",
            "type": "application"
        },
        "22": {
            "id": "22",
            "method": "create,read",
            "permission": "nexus:routes",
            "type": "application"
        },
        "25": {
            "id": "25",
            "method": "delete,read",
            "permission": "nexus:routes",
            "type": "application"
        },
        "23": {
            "id": "23",
            "method": "read",
            "permission": "nexus:routes",
            "type": "application"
        },
        "24": {
            "id": "24",
            "method": "update,read",
            "permission": "nexus:routes",
            "type": "application"
        },
        "67": {
            "id": "67",
            "method": "read",
            "permission": "nexus:repometa",
            "type": "application"
        },
        "45": {
            "id": "45",
            "method": "create,read",
            "permission": "nexus:targets",
            "type": "application"
        },
        "48": {
            "id": "48",
            "method": "delete,read",
            "permission": "nexus:targets",
            "type": "application"
        },
        "46": {
            "id": "46",
            "method": "read",
            "permission": "nexus:targets",
            "type": "application"
        },
        "47": {
            "id": "47",
            "method": "update,read",
            "permission": "nexus:targets",
            "type": "application"
        },
        "9": {
            "id": "9",
            "method": "create,read",
            "permission": "nexus:repotemplates",
            "type": "application"
        },
        "12": {
            "id": "12",
            "method": "delete,read",
            "permission": "nexus:repotemplates",
            "type": "application"
        },
        "10": {
            "id": "10",
            "method": "read",
            "permission": "nexus:repotemplates",
            "type": "application"
        },
        "11": {
            "id": "11",
            "method": "update,read",
            "permission": "nexus:repotemplates",
            "type": "application"
        },
        "74": {
            "id": "74",
            "method": "read",
            "permission": "nexus:componentsrepotypes",
            "type": "application"
        },
        "44": {
            "id": "44",
            "method": "read",
            "permission": "nexus:feeds",
            "type": "application"
        },
        "69": {
            "id": "69",
            "method": "read",
            "permission": "nexus:tasktypes",
            "type": "application"
        },
        "71": {
            "id": "71",
            "method": "read",
            "permission": "nexus:componentscheduletypes",
            "type": "application"
        },
        "26": {
            "id": "26",
            "method": "create,read",
            "permission": "nexus:tasks",
            "type": "application"
        },
        "29": {
            "id": "29",
            "method": "delete,read",
            "permission": "nexus:tasks",
            "type": "application"
        },
        "27": {
            "id": "27",
            "method": "read",
            "permission": "nexus:tasks",
            "type": "application"
        },
        "68": {
            "id": "68",
            "method": "read,delete",
            "permission": "nexus:tasksrun",
            "type": "application"
        },
        "28": {
            "id": "28",
            "method": "update,read",
            "permission": "nexus:tasks",
            "type": "application"
        },
        "17": {
            "id": "17",
            "method": "read",
            "permission": "nexus:index",
            "type": "application"
        },
        "1001": {
            "id": "1001",
            "method": "*",
            "permission": "security:*",
            "type": "application"
        },
        "3": {
            "id": "3",
            "method": "read",
            "permission": "nexus:settings",
            "type": "application"
        },
        "4": {
            "id": "4",
            "method": "update,read",
            "permission": "nexus:settings",
            "type": "application"
        },
        "49": {
            "id": "49",
            "method": "update,read",
            "permission": "nexus:status",
            "type": "application"
        },
        "1": {
            "id": "1",
            "method": "read",
            "permission": "nexus:status",
            "type": "application"
        },
        "56": {
            "id": "56",
            "method": "update",
            "permission": "nexus:repostatus",
            "type": "application"
        },
        "64": {
            "id": "64",
            "method": "create,read",
            "permission": "security:userschangepw",
            "type": "application"
        },
        "57": {
            "id": "57",
            "method": "create,read",
            "permission": "security:usersforgotpw",
            "type": "application"
        },
        "58": {
            "id": "58",
            "method": "create,read",
            "permission": "security:usersforgotid",
            "type": "application"
        },
        "75": {
            "id": "75",
            "method": "read",
            "permission": "security:componentsuserlocatortypes",
            "type": "application"
        },
        "80": {
            "id": "80",
            "method": "read",
            "permission": "security:privilegetypes",
            "type": "application"
        },
        "30": {
            "id": "30",
            "method": "create,read",
            "permission": "security:privileges",
            "type": "application"
        },
        "33": {
            "id": "33",
            "method": "delete,read",
            "permission": "security:privileges",
            "type": "application"
        },
        "31": {
            "id": "31",
            "method": "read",
            "permission": "security:privileges",
            "type": "application"
        },
        "32": {
            "id": "32",
            "method": "update,read",
            "permission": "security:privileges",
            "type": "application"
        },
        "59": {
            "id": "59",
            "method": "delete,read",
            "permission": "security:usersreset",
            "type": "application"
        },
        "34": {
            "id": "34",
            "method": "create,read",
            "permission": "security:roles",
            "type": "application"
        },
        "37": {
            "id": "37",
            "method": "delete,read",
            "permission": "security:roles",
            "type": "application"
        },
        "35": {
            "id": "35",
            "method": "read",
            "permission": "security:roles",
            "type": "application"
        },
        "36": {
            "id": "36",
            "method": "update,read",
            "permission": "security:roles",
            "type": "application"
        },
        "72": {
            "id": "72",
            "method": "create,read",
            "permission": "security:userssetpw",
            "type": "application"
        },
        "38": {
            "id": "38",
            "method": "create,read",
            "permission": "security:users",
            "type": "application"
        },
        "41": {
            "id": "41",
            "method": "delete,read",
            "permission": "security:users",
            "type": "application"
        },
        "39": {
            "id": "39",
            "method": "read",
            "permission": "security:users",
            "type": "application"
        },
        "40": {
            "id": "40",
            "method": "update,read",
            "permission": "security:users",
            "type": "application"
        },
        "51": {
            "id": "51",
            "method": "delete,read",
            "permission": "nexus:wastebasket",
            "type": "application"
        },
        "50": {
            "id": "50",
            "method": "read",
            "permission": "nexus:wastebasket",
            "type": "application"
        },
        "wonderland-all": {
            "id": "wonderland-all",
            "method": "*",
            "permission": "nexus:wonderland",
            "type": "application"
        },
        "yum-alias-read": {
            "id": "yum-alias-read",
            "method": "read",
            "permission": "nexus:yumAlias",
            "type": "application"
        },
        "yum-alias-create-read": {
            "id": "yum-alias-create-read",
            "method": "create,update,read",
            "permission": "nexus:yumAlias",
            "type": "application"
        },
        "yum-repository-read": {
            "id": "yum-repository-read",
            "method": "read",
            "permission": "nexus:yumVersionedRepositories",
            "type": "application"
        }
    }

def getBuiltinRoles(privmap):
    return {
        "analytics": {
            "groupName": "analytics",
            "description": "Gives access to Analytics",
            "privileges": [
                privmap["analytics-all"]
            ],
            "roles": [],
            "admin": False
        },
        "atlas": {
            "groupName": "atlas",
            "description": "Gives access to Atlas support tools",
            "privileges": [
                privmap["atlas-all"]
            ],
            "roles": [],
            "admin": False
        },
        "metrics-endpoints": {
            "groupName": "metrics-endpoints",
            "description": "Allows access to metrics endpoints.",
            "privileges": [
                privmap["metrics-endpoints"]
            ],
            "roles": [],
            "admin": False
        },
        "nx-admin": {
            "groupName": "nx-admin",
            "description": "Administration role for Nexus",
            "privileges": [
                privmap["1001"],
                privmap["1000"],
                privmap["83"]
            ],
            "roles": [],
            "admin": True
        },
        "anonymous": {
            "groupName": "anonymous",
            "description": "Anonymous role for Nexus",
            "privileges": [
                privmap["1"],
                privmap["57"],
                privmap["58"],
                privmap["70"],
                privmap["74"],
                privmap["54"]
            ],
            "roles": [
                "ui-healthcheck-read",
                "ui-search",
                "ui-repo-browser",
            ],
            "admin": False
        },
        "nx-apikey-access": {
            "groupName": "nx-apikey-access",
            "description": "API-Key Access role for Nexus.",
            "privileges": [
                privmap["83"]
            ],
            "roles": [],
            "admin": False
        },
        "nx-deployment": {
            "groupName": "nx-deployment",
            "description": "Deployment role for Nexus",
            "privileges": [
                privmap["83"]
            ],
            "roles": [
                "ui-basic",
                "anonymous",
            ],
            "admin": False
        },
        "nx-developer": {
            "groupName": "nx-developer",
            "description": "Developer role for Nexus",
            "privileges": [],
            "roles": [
                "ui-basic",
                "nx-deployment",
            ],
            "admin": False
        },
        "nexus-yum-admin": {
            "groupName": "nexus-yum-admin",
            "description": "Gives access to read versioned yum repositories and administrate version aliases",
            "privileges": [
                privmap["yum-repository-read"],
                privmap["yum-alias-create-read"],
                privmap["yum-alias-read"]
            ],
            "roles": [],
            "admin": False
        },
        "nexus-yum-user": {
            "groupName": "nexus-yum-user",
            "description": "Gives access to read versioned yum repositories",
            "privileges": [
                privmap["yum-repository-read"]
            ],
            "roles": [],
            "admin": False
        },
        "any-all-view": {
            "groupName": "any-all-view",
            "description": "Gives access to view ALL Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False
        },
        "repo-all-full": {
            "groupName": "repo-all-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL Maven1 and Maven2 repositories in Nexus.",
            "privileges": [
                privmap["T4"],
                privmap["T5"],
                privmap["T6"],
                privmap["T7"],
                privmap["T8"],
                privmap["repository-all"],
                privmap["T1"],
                privmap["T2"],
                privmap["T3"]
            ],
            "roles": [],
            "admin": False
        },
        "repo-all-read": {
            "groupName": "repo-all-read",
            "description": "Gives access to read ALL content of ALL Maven1 and Maven2 repositories in Nexus.",
            "privileges": [
                privmap["repository-all"],
                privmap["T1"],
                privmap["T2"]
            ],
            "roles": [],
            "admin": False
        },
        "maven1-all-view": {
            "groupName": "maven1-all-view",
            "description": "Gives access to view ALL Maven1 Repositories in Nexus.",
            "privileges": [
                privmap["repository-central-m1"]
            ],
            "roles": [],
            "admin": False
        },
        "maven2-all-view": {
            "groupName": "maven2-all-view",
            "description": "Gives access to view ALL Maven2 Repositories in Nexus.",
            "privileges": [
                privmap["repository-thirdparty"],
                privmap["repository-public"],
                privmap["repository-snapshots"],
                privmap["repository-releases"],
                privmap["repository-apache-snapshots"],
                privmap["repository-central"]
            ],
            "roles": [],
            "admin": False
        },
        "npm-all-full": {
            "groupName": "npm-all-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL npm Repositories in Nexus.",
            "privileges": [
                privmap["npm-read"],
                privmap["npm-create"],
                privmap["npm-delete"],
                privmap["npm-update"]
            ],
            "roles": [
                "npm-all-view",
            ],
            "admin": False
        },
        "npm-all-read": {
            "groupName": "npm-all-read",
            "description": "Gives access to read ALL content of ALL npm Repositories in Nexus.",
            "privileges": [
                privmap["npm-read"]
            ],
            "roles": [
                "npm-all-view",
            ],
            "admin": False
        },
        "npm-all-view": {
            "groupName": "npm-all-view",
            "description": "Gives access to view ALL npm Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False
        },
        "nuget-all-full": {
            "groupName": "nuget-all-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL NuGet Repositories in Nexus.",
            "privileges": [
                privmap["nuget-read"],
                privmap["nuget-create"],
                privmap["nuget-delete"],
                privmap["nuget-update"]
            ],
            "roles": [
                "nuget-all-view",
            ],
            "admin": False
        },
        "nuget-all-read": {
            "groupName": "nuget-all-read",
            "description": "Gives access to read ALL content of ALL NuGet Repositories in Nexus.",
            "privileges": [
                privmap["nuget-read"]
            ],
            "roles": [
                "nuget-all-view",
            ],
            "admin": False
        },
        "nuget-all-view": {
            "groupName": "nuget-all-view",
            "description": "Gives access to view ALL NuGet Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False
        },
        "repository-any-full": {
            "groupName": "repository-any-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL repositories in Nexus.",
            "privileges": [
                privmap["T10"],
                privmap["T12"],
                privmap["repository-all"],
                privmap["T9"],
                privmap["T11"]
            ],
            "roles": [],
            "admin": False
        },
        "repository-any-read": {
            "groupName": "repository-any-read",
            "description": "Gives access to read ALL content of ALL repositories in Nexus.",
            "privileges": [
                privmap["repository-all"],
                privmap["T9"]
            ],
            "roles": [],
            "admin": False
        },
        "rubygems-all-full": {
            "groupName": "rubygems-all-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL Rubygems Repositories in Nexus.",
            "privileges": [
                privmap["rubygems-create"],
                privmap["rubygems-delete"],
                privmap["rubygems-read"],
                privmap["rubygems-update"]
            ],
            "roles": [
                "rubygems-all-view",
            ],
            "admin": False
        },
        "rubygems-all-read": {
            "groupName": "rubygems-all-read",
            "description": "Gives access to read ALL content of ALL Rubygems Repositories in Nexus.",
            "privileges": [
                privmap["rubygems-read"]
            ],
            "roles": [
                "rubygems-all-view",
            ],
            "admin": False
        },
        "rubygems-all-view": {
            "groupName": "rubygems-all-view",
            "description": "Gives access to view ALL Rubygems Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False
        },
        "site-all-full": {
            "groupName": "site-all-full",
            "description": "Gives access to create/read/update/delete ALL content of ALL Site Repositories in Nexus.",
            "privileges": [
                privmap["site-create"],
                privmap["site-update"],
                privmap["site-delete"],
                privmap["repository-all"],
                privmap["site-read"]
            ],
            "roles": [],
            "admin": False
        },
        "site-all-read": {
            "groupName": "site-all-read",
            "description": "Gives access to read ALL content of ALL Site Repositories in Nexus.",
            "privileges": [
                privmap["repository-all"],
                privmap["site-read"]
            ],
            "roles": [],
            "admin": False
        },
        "site-all-view": {
            "groupName": "site-all-view",
            "description": "Gives access to view ALL Site Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False
        },
        "ui-basic": {
            "groupName": "ui-basic",
            "description": "Generic privileges for users in the Nexus UI",
            "privileges": [
                privmap["1"],
                privmap["2"],
                privmap["64"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-capabilities-admin": {
            "groupName": "ui-capabilities-admin",
            "description": "Gives access to Capabilities Administration screen in Nexus UI",
            "privileges": [
                privmap["capabilities-read"],
                privmap["capability-types-read"],
                privmap["14"],
                privmap["capabilities-update-read"],
                privmap["6"],
                privmap["capabilities-delete-read"],
                privmap["capabilities-create-read"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-group-admin": {
            "groupName": "ui-group-admin",
            "description": "Gives access to the Group Administration screen in Nexus UI",
            "privileges": [
                privmap["13"],
                privmap["14"],
                privmap["15"],
                privmap["repository-all"],
                privmap["16"],
                privmap["6"]
            ],
            "roles": [
                "ui-repo-browser",
            ],
            "admin": False
        },
        "ui-healthcheck-full": {
            "groupName": "ui-healthcheck-full",
            "description": "Gives access to view and enable/disable the health check for repositories, along with some additional artifact data",
            "privileges": [
                privmap["nexus-healthcheck-update"]
            ],
            "roles": [
                "ui-healthcheck-read",
            ],
            "admin": False
        },
        "ui-healthcheck-read": {
            "groupName": "ui-healthcheck-read",
            "description": "Gives access to view the health check summary for repositories",
            "privileges": [
                privmap["nexus-healthcheck-summary-read"],
                privmap["nexus-healthcheck-read"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-ldap-admin": {
            "groupName": "ui-ldap-admin",
            "description": "Gives access to configure the LDAP server used for authentication.",
            "privileges": [
                privmap["ldap-conn-read"],
                privmap["ldap-user-group-conf-update"],
                privmap["ldap-user-role-map-create"],
                privmap["ldap-conn-update"],
                privmap["ldap-test-auth-conf"],
                privmap["ldap-user-role-map-update"],
                privmap["ldap-user-role-map-read"],
                privmap["ldap-user-role-map-delete"],
                privmap["ldap-user-group-conf-read"],
                privmap["ldap-test-user-group-conf"]
            ],
            "roles": [
                "ui-server-admin",
            ],
            "admin": False
        },
        "ui-logs-config-files": {
            "groupName": "ui-logs-config-files",
            "description": "Gives access to the Logs and Config Files screen in Nexus UI",
            "privileges": [
                privmap["42"],
                privmap["43"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-plugin-console": {
            "groupName": "ui-plugin-console",
            "description": "Gives access to the Plugin Console screen in Nexus UI.",
            "privileges": [
                privmap["plugin-infos-read"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-privileges-admin": {
            "groupName": "ui-privileges-admin",
            "description": "Gives access to the Privilege Administration screen in Nexus UI",
            "privileges": [
                privmap["33"],
                privmap["46"],
                privmap["14"],
                privmap["6"],
                privmap["80"],
                privmap["30"],
                privmap["31"],
                privmap["32"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-repository-admin": {
            "groupName": "ui-repository-admin",
            "description": "Gives access to the Repository Administration screen in Nexus UI",
            "privileges": [
                privmap["78"],
                privmap["79"],
                privmap["repository-all"],
                privmap["5"],
                privmap["6"],
                privmap["7"],
                privmap["8"],
                privmap["81"],
                privmap["82"],
                privmap["74"],
                privmap["10"]
            ],
            "roles": [
                "ui-repo-browser",
            ],
            "admin": False
        },
        "ui-repo-browser": {
            "groupName": "ui-repo-browser",
            "description": "Gives access to the Repository Browser screen in Nexus UI",
            "privileges": [
                privmap["55"],
                privmap["14"],
                privmap["6"],
                privmap["browse-remote-repo"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-repository-targets-admin": {
            "groupName": "ui-repository-targets-admin",
            "description": "Gives access to the Repository Target Administration screen in Nexus UI",
            "privileges": [
                privmap["45"],
                privmap["46"],
                privmap["47"],
                privmap["48"],
                privmap["70"],
                privmap["74"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-roles-admin": {
            "groupName": "ui-roles-admin",
            "description": "Gives access to the Role Administration screen in Nexus UI",
            "privileges": [
                privmap["34"],
                privmap["35"],
                privmap["36"],
                privmap["37"],
                privmap["31"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-routing-admin": {
            "groupName": "ui-routing-admin",
            "description": "Gives access to the Routing Administration screen in Nexus UI",
            "privileges": [
                privmap["22"],
                privmap["23"],
                privmap["24"],
                privmap["14"],
                privmap["25"],
                privmap["6"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-scheduled-tasks-admin": {
            "groupName": "ui-scheduled-tasks-admin",
            "description": "Gives access to the Scheduled Task Administration screen in Nexus UI",
            "privileges": [
                privmap["68"],
                privmap["14"],
                privmap["69"],
                privmap["26"],
                privmap["27"],
                privmap["6"],
                privmap["28"],
                privmap["29"],
                privmap["71"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-search": {
            "groupName": "ui-search",
            "description": "Gives access to the Search screen in Nexus UI",
            "privileges": [
                privmap["17"],
                privmap["19"],
                privmap["54"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-server-admin": {
            "groupName": "ui-server-admin",
            "description": "Gives access to the Server Administration screen in Nexus UI",
            "privileges": [
                privmap["3"],
                privmap["4"],
                privmap["73"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-system-feeds": {
            "groupName": "ui-system-feeds",
            "description": "Gives access to the System Feeds screen in Nexus UI",
            "privileges": [
                privmap["44"]
            ],
            "roles": [],
            "admin": False
        },
        "ui-users-admin": {
            "groupName": "ui-users-admin",
            "description": "Gives access to the User Administration screen in Nexus UI",
            "privileges": [
                privmap["35"],
                privmap["38"],
                privmap["39"],
                privmap["72"],
                privmap["40"],
                privmap["41"],
                privmap["75"]
            ],
            "roles": [],
            "admin": False
        },
        "wonderland": {
            "groupName": "wonderland",
            "description": "Gives access to Wonderland",
            "privileges": [
                privmap["wonderland-all"]
            ],
            "roles": [],
            "admin": False
        }
    }
