def getBuiltinTargs():
    return {
        "1": {
            "name": "1",
            "ptype": "maven2",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "2": {
            "name": "2",
            "ptype": "maven1",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "3": {
            "name": "3",
            "ptype": "maven2",
            "patterns": ["(?!.*-sources.*).*"],
            "defincpat": ["**"],
            "defexcpat": ["**/*-sources.*/**"]
        },
        "4": {
            "name": "4",
            "ptype": "maven2",
            "patterns": [".*maven-metadata\.xml.*"],
            "defincpat": ["**/*maven-metadata.xml*"],
            "defexcpat": []
        },
        "any": {
            "name": "any",
            "ptype": "any",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "site": {
            "name": "site",
            "ptype": "site",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "npm": {
            "name": "npm",
            "ptype": "npm",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "nuget": {
            "name": "nuget",
            "ptype": "nuget",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        },
        "rubygems": {
            "name": "rubygems",
            "ptype": "rubygems",
            "patterns": [".*"],
            "defincpat": ["**"],
            "defexcpat": []
        }
    }

def getBuiltinPrivs(targs):
    return {
        "All M1 Repositories": {
            "name": "All M1 Repositories",
            "target": targs["2"],
            "repo": "*",
            "builtin": True
        },
        "All M2 Repositories": {
            "name": "All M2 Repositories",
            "target": targs["1"],
            "repo": "*",
            "builtin": True
        },
        "All npm Repositories": {
            "name": "All npm Repositories",
            "target": targs["npm"],
            "repo": "*",
            "builtin": True
        },
        "All NuGet Repositories": {
            "name": "All NuGet Repositories",
            "target": targs["nuget"],
            "repo": "*",
            "builtin": True
        },
        "All Repositories": {
            "name": "All Repositories",
            "target": targs["any"],
            "repo": "*",
            "builtin": True
        },
        "All Rubygems Repositories": {
            "name": "All Rubygems Repositories",
            "target": targs["rubygems"],
            "repo": "*",
            "builtin": True
        },
        "All Site Repositories": {
            "name": "All Site Repositories",
            "target": targs["site"],
            "repo": "*",
            "builtin": True
        }
    }

def getBuiltinPrivmap(privs):
    return {
        "repository-all": {
            "id": "repository-all",
            "repo": "*",
            "type": "view",
            "needadmin": False
        },
        "T6": {
            "id": "T6",
            "method": "create",
            "priv": privs["All M1 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T8": {
            "id": "T8",
            "method": "delete",
            "priv": privs["All M1 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T2": {
            "id": "T2",
            "method": "read",
            "priv": privs["All M1 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T4": {
            "id": "T4",
            "method": "update",
            "priv": privs["All M1 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T5": {
            "id": "T5",
            "method": "create",
            "priv": privs["All M2 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T7": {
            "id": "T7",
            "method": "delete",
            "priv": privs["All M2 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T1": {
            "id": "T1",
            "method": "read",
            "priv": privs["All M2 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T3": {
            "id": "T3",
            "method": "update",
            "priv": privs["All M2 Repositories"],
            "type": "target",
            "needadmin": False
        },
        "npm-create": {
            "id": "npm-create",
            "method": "create",
            "priv": privs["All npm Repositories"],
            "type": "target",
            "needadmin": False
        },
        "npm-delete": {
            "id": "npm-delete",
            "method": "delete",
            "priv": privs["All npm Repositories"],
            "type": "target",
            "needadmin": False
        },
        "npm-read": {
            "id": "npm-read",
            "method": "read",
            "priv": privs["All npm Repositories"],
            "type": "target",
            "needadmin": False
        },
        "npm-update": {
            "id": "npm-update",
            "method": "update",
            "priv": privs["All npm Repositories"],
            "type": "target",
            "needadmin": False
        },
        "nuget-create": {
            "id": "nuget-create",
            "method": "create",
            "priv": privs["All NuGet Repositories"],
            "type": "target",
            "needadmin": False
        },
        "nuget-delete": {
            "id": "nuget-delete",
            "method": "delete",
            "priv": privs["All NuGet Repositories"],
            "type": "target",
            "needadmin": False
        },
        "nuget-read": {
            "id": "nuget-read",
            "method": "read",
            "priv": privs["All NuGet Repositories"],
            "type": "target",
            "needadmin": False
        },
        "nuget-update": {
            "id": "nuget-update",
            "method": "update",
            "priv": privs["All NuGet Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T11": {
            "id": "T11",
            "method": "create",
            "priv": privs["All Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T12": {
            "id": "T12",
            "method": "delete",
            "priv": privs["All Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T9": {
            "id": "T9",
            "method": "read",
            "priv": privs["All Repositories"],
            "type": "target",
            "needadmin": False
        },
        "T10": {
            "id": "T10",
            "method": "update",
            "priv": privs["All Repositories"],
            "type": "target",
            "needadmin": False
        },
        "rubygems-create": {
            "id": "rubygems-create",
            "method": "create",
            "priv": privs["All Rubygems Repositories"],
            "type": "target",
            "needadmin": False
        },
        "rubygems-delete": {
            "id": "rubygems-delete",
            "method": "delete",
            "priv": privs["All Rubygems Repositories"],
            "type": "target",
            "needadmin": False
        },
        "rubygems-read": {
            "id": "rubygems-read",
            "method": "read",
            "priv": privs["All Rubygems Repositories"],
            "type": "target",
            "needadmin": False
        },
        "rubygems-update": {
            "id": "rubygems-update",
            "method": "update",
            "priv": privs["All Rubygems Repositories"],
            "type": "target",
            "needadmin": False
        },
        "site-create": {
            "id": "site-create",
            "method": "create",
            "priv": privs["All Site Repositories"],
            "type": "target",
            "needadmin": False
        },
        "site-delete": {
            "id": "site-delete",
            "method": "delete",
            "priv": privs["All Site Repositories"],
            "type": "target",
            "needadmin": False
        },
        "site-read": {
            "id": "site-read",
            "method": "read",
            "priv": privs["All Site Repositories"],
            "type": "target",
            "needadmin": False
        },
        "site-update": {
            "id": "site-update",
            "method": "update",
            "priv": privs["All Site Repositories"],
            "type": "target",
            "needadmin": False
        },
        "1000": {
            "id": "1000",
            "method": "*",
            "permission": "nexus:*",
            "type": "application",
            "needadmin": True
        },
        "analytics-all": {
            "id": "analytics-all",
            "method": "*",
            "permission": "nexus:analytics",
            "type": "application",
            "needadmin": False
        },
        "83": {
            "id": "83",
            "method": "*",
            "permission": "apikey:access",
            "type": "application",
            "needadmin": False
        },
        "54": {
            "id": "54",
            "method": "read",
            "permission": "nexus:artifact",
            "type": "application",
            "needadmin": False
        },
        "65": {
            "id": "65",
            "method": "create,read",
            "permission": "nexus:artifact",
            "type": "application",
            "needadmin": False
        },
        "atlas-all": {
            "id": "atlas-all",
            "method": "*",
            "permission": "nexus:atlas",
            "type": "application",
            "needadmin": False
        },
        "browse-remote-repo": {
            "id": "browse-remote-repo",
            "method": "read",
            "permission": "nexus:browseremote",
            "type": "application",
            "needadmin": False
        },
        "capabilities-create-read": {
            "id": "capabilities-create-read",
            "method": "create,read",
            "permission": "nexus:capabilities",
            "type": "application",
            "needadmin": False
        },
        "capabilities-delete-read": {
            "id": "capabilities-delete-read",
            "method": "delete,read",
            "permission": "nexus:capabilities",
            "type": "application",
            "needadmin": False
        },
        "capabilities-read": {
            "id": "capabilities-read",
            "method": "read",
            "permission": "nexus:capabilities",
            "type": "application",
            "needadmin": False
        },
        "capabilities-update-read": {
            "id": "capabilities-update-read",
            "method": "update,read",
            "permission": "nexus:capabilities",
            "type": "application",
            "needadmin": False
        },
        "capability-types-read": {
            "id": "capability-types-read",
            "method": "read",
            "permission": "nexus:capabilityTypes",
            "type": "application",
            "needadmin": False
        },
        "19": {
            "id": "19",
            "method": "read",
            "permission": "nexus:identify",
            "type": "application",
            "needadmin": False
        },
        "21": {
            "id": "21",
            "method": "delete,read",
            "permission": "nexus:cache",
            "type": "application",
            "needadmin": True
        },
        "43": {
            "id": "43",
            "method": "read",
            "permission": "nexus:configuration",
            "type": "application",
            "needadmin": False
        },
        "nexus-healthcheck-read": {
            "id": "nexus-healthcheck-read",
            "method": "read",
            "permission": "nexus:healthcheck",
            "type": "application",
            "needadmin": False
        },
        "nexus-healthcheck-update": {
            "id": "nexus-healthcheck-update",
            "method": "update",
            "permission": "nexus:healthcheck",
            "type": "application",
            "needadmin": False
        },
        "nexus-healthcheck-summary-read": {
            "id": "nexus-healthcheck-summary-read",
            "method": "read",
            "permission": "nexus:healthchecksummary",
            "type": "application",
            "needadmin": False
        },
        "ldap-conn-read": {
            "id": "ldap-conn-read",
            "method": "read",
            "permission": "nexus:ldapconninfo",
            "type": "application",
            "needadmin": False
        },
        "ldap-conn-update": {
            "id": "ldap-conn-update",
            "method": "update",
            "permission": "nexus:ldapconninfo",
            "type": "application",
            "needadmin": True
        },
        "ldap-test-auth-conf": {
            "id": "ldap-test-auth-conf",
            "method": "update",
            "permission": "nexus:ldaptestauth",
            "type": "application",
            "needadmin": True
        },
        "ldap-test-user-group-conf": {
            "id": "ldap-test-user-group-conf",
            "method": "update",
            "permission": "nexus:ldaptestuserconf",
            "type": "application",
            "needadmin": True
        },
        "ldap-user-group-conf-read": {
            "id": "ldap-user-group-conf-read",
            "method": "read",
            "permission": "nexus:ldapusergroupconf",
            "type": "application",
            "needadmin": False
        },
        "ldap-user-group-conf-update": {
            "id": "ldap-user-group-conf-update",
            "method": "update",
            "permission": "nexus:ldapusergroupconf",
            "type": "application",
            "needadmin": True
        },
        "ldap-user-role-map-create": {
            "id": "ldap-user-role-map-create",
            "method": "create",
            "permission": "nexus:ldapuserrolemap",
            "type": "application",
            "needadmin": True
        },
        "ldap-user-role-map-delete": {
            "id": "ldap-user-role-map-delete",
            "method": "delete,read",
            "permission": "nexus:ldapuserrolemap",
            "type": "application",
            "needadmin": True
        },
        "ldap-user-role-map-read": {
            "id": "ldap-user-role-map-read",
            "method": "read",
            "permission": "nexus:ldapuserrolemap",
            "type": "application",
            "needadmin": False
        },
        "ldap-user-role-map-update": {
            "id": "ldap-user-role-map-update",
            "method": "update",
            "permission": "nexus:ldapuserrolemap",
            "type": "application",
            "needadmin": True
        },
        "77": {
            "id": "77",
            "method": "read,update",
            "permission": "nexus:logconfig",
            "type": "application",
            "needadmin": False
        },
        "2": {
            "id": "2",
            "method": "read",
            "permission": "nexus:authentication",
            "type": "application",
            "needadmin": False
        },
        "42": {
            "id": "42",
            "method": "read",
            "permission": "nexus:logs",
            "type": "application",
            "needadmin": False
        },
        "metrics-endpoints": {
            "id": "metrics-endpoints",
            "method": "*",
            "permission": "nexus:metrics-endpoints",
            "type": "application",
            "needadmin": False
        },
        "66": {
            "id": "66",
            "method": "update,read",
            "permission": "nexus:command",
            "type": "application",
            "needadmin": False
        },
        "plugin-infos-read": {
            "id": "plugin-infos-read",
            "method": "read",
            "permission": "nexus:pluginconsoleplugininfos",
            "type": "application",
            "needadmin": False
        },
        "55": {
            "id": "55",
            "method": "read",
            "permission": "nexus:repostatus",
            "type": "application",
            "needadmin": False
        },
        "73": {
            "id": "73",
            "method": "read",
            "permission": "nexus:componentrealmtypes",
            "type": "application",
            "needadmin": False
        },
        "76": {
            "id": "76",
            "method": "delete,read",
            "permission": "nexus:metadata",
            "type": "application",
            "needadmin": False
        },
        "20": {
            "id": "20",
            "method": "delete,read",
            "permission": "nexus:attributes",
            "type": "application",
            "needadmin": False
        },
        "18": {
            "id": "18",
            "method": "delete,read",
            "permission": "nexus:index",
            "type": "application",
            "needadmin": False
        },
        "5": {
            "id": "5",
            "method": "create,read",
            "permission": "nexus:repositories",
            "type": "application",
            "needadmin": True
        },
        "8": {
            "id": "8",
            "method": "delete,read",
            "permission": "nexus:repositories",
            "type": "application",
            "needadmin": True
        },
        "6": {
            "id": "6",
            "method": "read",
            "permission": "nexus:repositories",
            "type": "application",
            "needadmin": False
        },
        "7": {
            "id": "7",
            "method": "update,read",
            "permission": "nexus:repositories",
            "type": "application",
            "needadmin": True
        },
        "70": {
            "id": "70",
            "method": "read",
            "permission": "nexus:componentscontentclasses",
            "type": "application",
            "needadmin": False
        },
        "13": {
            "id": "13",
            "method": "create,read",
            "permission": "nexus:repogroups",
            "type": "application",
            "needadmin": True
        },
        "16": {
            "id": "16",
            "method": "delete,read",
            "permission": "nexus:repogroups",
            "type": "application",
            "needadmin": True
        },
        "14": {
            "id": "14",
            "method": "read",
            "permission": "nexus:repogroups",
            "type": "application",
            "needadmin": False
        },
        "15": {
            "id": "15",
            "method": "update,read",
            "permission": "nexus:repogroups",
            "type": "application",
            "needadmin": True
        },
        "79": {
            "id": "79",
            "method": "create,read",
            "permission": "nexus:repositorymirrors",
            "type": "application",
            "needadmin": False
        },
        "78": {
            "id": "78",
            "method": "read",
            "permission": "nexus:repositorymirrors",
            "type": "application",
            "needadmin": False
        },
        "82": {
            "id": "82",
            "method": "read",
            "permission": "nexus:repositorymirrorsstatus",
            "type": "application",
            "needadmin": False
        },
        "81": {
            "id": "81",
            "method": "read",
            "permission": "nexus:repositorypredefinedmirrors",
            "type": "application",
            "needadmin": False
        },
        "22": {
            "id": "22",
            "method": "create,read",
            "permission": "nexus:routes",
            "type": "application",
            "needadmin": False
        },
        "25": {
            "id": "25",
            "method": "delete,read",
            "permission": "nexus:routes",
            "type": "application",
            "needadmin": False
        },
        "23": {
            "id": "23",
            "method": "read",
            "permission": "nexus:routes",
            "type": "application",
            "needadmin": False
        },
        "24": {
            "id": "24",
            "method": "update,read",
            "permission": "nexus:routes",
            "type": "application",
            "needadmin": False
        },
        "67": {
            "id": "67",
            "method": "read",
            "permission": "nexus:repometa",
            "type": "application",
            "needadmin": False
        },
        "45": {
            "id": "45",
            "method": "create,read",
            "permission": "nexus:targets",
            "type": "application",
            "needadmin": True
        },
        "48": {
            "id": "48",
            "method": "delete,read",
            "permission": "nexus:targets",
            "type": "application",
            "needadmin": True
        },
        "46": {
            "id": "46",
            "method": "read",
            "permission": "nexus:targets",
            "type": "application",
            "needadmin": False
        },
        "47": {
            "id": "47",
            "method": "update,read",
            "permission": "nexus:targets",
            "type": "application",
            "needadmin": True
        },
        "9": {
            "id": "9",
            "method": "create,read",
            "permission": "nexus:repotemplates",
            "type": "application",
            "needadmin": False
        },
        "12": {
            "id": "12",
            "method": "delete,read",
            "permission": "nexus:repotemplates",
            "type": "application",
            "needadmin": False
        },
        "10": {
            "id": "10",
            "method": "read",
            "permission": "nexus:repotemplates",
            "type": "application",
            "needadmin": False
        },
        "11": {
            "id": "11",
            "method": "update,read",
            "permission": "nexus:repotemplates",
            "type": "application",
            "needadmin": False
        },
        "74": {
            "id": "74",
            "method": "read",
            "permission": "nexus:componentsrepotypes",
            "type": "application",
            "needadmin": False
        },
        "44": {
            "id": "44",
            "method": "read",
            "permission": "nexus:feeds",
            "type": "application",
            "needadmin": False
        },
        "69": {
            "id": "69",
            "method": "read",
            "permission": "nexus:tasktypes",
            "type": "application",
            "needadmin": False
        },
        "71": {
            "id": "71",
            "method": "read",
            "permission": "nexus:componentscheduletypes",
            "type": "application",
            "needadmin": False
        },
        "26": {
            "id": "26",
            "method": "create,read",
            "permission": "nexus:tasks",
            "type": "application",
            "needadmin": True
        },
        "29": {
            "id": "29",
            "method": "delete,read",
            "permission": "nexus:tasks",
            "type": "application",
            "needadmin": True
        },
        "27": {
            "id": "27",
            "method": "read",
            "permission": "nexus:tasks",
            "type": "application",
            "needadmin": False
        },
        "68": {
            "id": "68",
            "method": "read,delete",
            "permission": "nexus:tasksrun",
            "type": "application",
            "needadmin": True
        },
        "28": {
            "id": "28",
            "method": "update,read",
            "permission": "nexus:tasks",
            "type": "application",
            "needadmin": True
        },
        "17": {
            "id": "17",
            "method": "read",
            "permission": "nexus:index",
            "type": "application",
            "needadmin": False
        },
        "1001": {
            "id": "1001",
            "method": "*",
            "permission": "security:*",
            "type": "application",
            "needadmin": True
        },
        "3": {
            "id": "3",
            "method": "read",
            "permission": "nexus:settings",
            "type": "application",
            "needadmin": False
        },
        "4": {
            "id": "4",
            "method": "update,read",
            "permission": "nexus:settings",
            "type": "application",
            "needadmin": True
        },
        "49": {
            "id": "49",
            "method": "update,read",
            "permission": "nexus:status",
            "type": "application",
            "needadmin": True
        },
        "1": {
            "id": "1",
            "method": "read",
            "permission": "nexus:status",
            "type": "application",
            "needadmin": False
        },
        "56": {
            "id": "56",
            "method": "update",
            "permission": "nexus:repostatus",
            "type": "application",
            "needadmin": True
        },
        "64": {
            "id": "64",
            "method": "create,read",
            "permission": "security:userschangepw",
            "type": "application",
            "needadmin": False
        },
        "57": {
            "id": "57",
            "method": "create,read",
            "permission": "security:usersforgotpw",
            "type": "application",
            "needadmin": False
        },
        "58": {
            "id": "58",
            "method": "create,read",
            "permission": "security:usersforgotid",
            "type": "application",
            "needadmin": False
        },
        "75": {
            "id": "75",
            "method": "read",
            "permission": "security:componentsuserlocatortypes",
            "type": "application",
            "needadmin": False
        },
        "80": {
            "id": "80",
            "method": "read",
            "permission": "security:privilegetypes",
            "type": "application",
            "needadmin": False
        },
        "30": {
            "id": "30",
            "method": "create,read",
            "permission": "security:privileges",
            "type": "application",
            "needadmin": True
        },
        "33": {
            "id": "33",
            "method": "delete,read",
            "permission": "security:privileges",
            "type": "application",
            "needadmin": True
        },
        "31": {
            "id": "31",
            "method": "read",
            "permission": "security:privileges",
            "type": "application",
            "needadmin": False
        },
        "32": {
            "id": "32",
            "method": "update,read",
            "permission": "security:privileges",
            "type": "application",
            "needadmin": True
        },
        "59": {
            "id": "59",
            "method": "delete,read",
            "permission": "security:usersreset",
            "type": "application",
            "needadmin": True
        },
        "34": {
            "id": "34",
            "method": "create,read",
            "permission": "security:roles",
            "type": "application",
            "needadmin": True
        },
        "37": {
            "id": "37",
            "method": "delete,read",
            "permission": "security:roles",
            "type": "application",
            "needadmin": True
        },
        "35": {
            "id": "35",
            "method": "read",
            "permission": "security:roles",
            "type": "application",
            "needadmin": False
        },
        "36": {
            "id": "36",
            "method": "update,read",
            "permission": "security:roles",
            "type": "application",
            "needadmin": True
        },
        "72": {
            "id": "72",
            "method": "create,read",
            "permission": "security:userssetpw",
            "type": "application",
            "needadmin": True
        },
        "38": {
            "id": "38",
            "method": "create,read",
            "permission": "security:users",
            "type": "application",
            "needadmin": True
        },
        "41": {
            "id": "41",
            "method": "delete,read",
            "permission": "security:users",
            "type": "application",
            "needadmin": True
        },
        "39": {
            "id": "39",
            "method": "read",
            "permission": "security:users",
            "type": "application",
            "needadmin": False
        },
        "40": {
            "id": "40",
            "method": "update,read",
            "permission": "security:users",
            "type": "application",
            "needadmin": True
        },
        "51": {
            "id": "51",
            "method": "delete,read",
            "permission": "nexus:wastebasket",
            "type": "application",
            "needadmin": False
        },
        "50": {
            "id": "50",
            "method": "read",
            "permission": "nexus:wastebasket",
            "type": "application",
            "needadmin": False
        },
        "wonderland-all": {
            "id": "wonderland-all",
            "method": "*",
            "permission": "nexus:wonderland",
            "type": "application",
            "needadmin": False
        },
        "yum-alias-read": {
            "id": "yum-alias-read",
            "method": "read",
            "permission": "nexus:yumAlias",
            "type": "application",
            "needadmin": False
        },
        "yum-alias-create-read": {
            "id": "yum-alias-create-read",
            "method": "create,update,read",
            "permission": "nexus:yumAlias",
            "type": "application",
            "needadmin": False
        },
        "yum-repository-read": {
            "id": "yum-repository-read",
            "method": "read",
            "permission": "nexus:yumVersionedRepositories",
            "type": "application",
            "needadmin": False
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
            "admin": False,
            "builtin": True
        },
        "atlas": {
            "groupName": "atlas",
            "description": "Gives access to Atlas support tools",
            "privileges": [
                privmap["atlas-all"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
        },
        "metrics-endpoints": {
            "groupName": "metrics-endpoints",
            "description": "Allows access to metrics endpoints.",
            "privileges": [
                privmap["metrics-endpoints"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": True,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "nx-apikey-access": {
            "groupName": "nx-apikey-access",
            "description": "API-Key Access role for Nexus.",
            "privileges": [
                privmap["83"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "nx-developer": {
            "groupName": "nx-developer",
            "description": "Developer role for Nexus",
            "privileges": [],
            "roles": [
                "ui-basic",
                "nx-deployment",
            ],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "nexus-yum-user": {
            "groupName": "nexus-yum-user",
            "description": "Gives access to read versioned yum repositories",
            "privileges": [
                privmap["yum-repository-read"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
        },
        "any-all-view": {
            "groupName": "any-all-view",
            "description": "Gives access to view ALL Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "maven1-all-view": {
            "groupName": "maven1-all-view",
            "description": "Gives access to view ALL Maven1 Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
        },
        "maven2-all-view": {
            "groupName": "maven2-all-view",
            "description": "Gives access to view ALL Maven2 Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "npm-all-view": {
            "groupName": "npm-all-view",
            "description": "Gives access to view ALL npm Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "nuget-all-view": {
            "groupName": "nuget-all-view",
            "description": "Gives access to view ALL NuGet Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "repository-any-read": {
            "groupName": "repository-any-read",
            "description": "Gives access to read ALL content of ALL repositories in Nexus.",
            "privileges": [
                privmap["repository-all"],
                privmap["T9"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "rubygems-all-view": {
            "groupName": "rubygems-all-view",
            "description": "Gives access to view ALL Rubygems Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "site-all-read": {
            "groupName": "site-all-read",
            "description": "Gives access to read ALL content of ALL Site Repositories in Nexus.",
            "privileges": [
                privmap["repository-all"],
                privmap["site-read"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
        },
        "site-all-view": {
            "groupName": "site-all-view",
            "description": "Gives access to view ALL Site Repositories in Nexus.",
            "privileges": [],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "ui-healthcheck-read": {
            "groupName": "ui-healthcheck-read",
            "description": "Gives access to view the health check summary for repositories",
            "privileges": [
                privmap["nexus-healthcheck-summary-read"],
                privmap["nexus-healthcheck-read"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "ui-logs-config-files": {
            "groupName": "ui-logs-config-files",
            "description": "Gives access to the Logs and Config Files screen in Nexus UI",
            "privileges": [
                privmap["42"],
                privmap["43"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
        },
        "ui-plugin-console": {
            "groupName": "ui-plugin-console",
            "description": "Gives access to the Plugin Console screen in Nexus UI.",
            "privileges": [
                privmap["plugin-infos-read"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "ui-system-feeds": {
            "groupName": "ui-system-feeds",
            "description": "Gives access to the System Feeds screen in Nexus UI",
            "privileges": [
                privmap["44"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
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
            "admin": False,
            "builtin": True
        },
        "wonderland": {
            "groupName": "wonderland",
            "description": "Gives access to Wonderland",
            "privileges": [
                privmap["wonderland-all"]
            ],
            "roles": [],
            "admin": False,
            "builtin": True
        }
    }
