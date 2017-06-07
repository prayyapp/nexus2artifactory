hlp = {
    # Main Menu
    "Initial Setup": """
The initial setup required to proceed with the rest of the migration. This
should be configured first, before anything else. The information in this menu
allows the tool to connect to both Nexus and Artifactory, so that it can
properly configure and execute the migration.""",
    "Repository Migration Setup": """
Set up migration for repositories. Choose which repositories are to be migrated
and which are not, and modify those repositories' details as necessary.""",
    "Security Migration Setup": """
Set up migration for security settings, including users, groups, permissions,
and LDAP settings.""",
    "Options Migration Setup": """
Set up migration for miscellaneous options. None are implemented yet.""",
    "Save Configuration": """
Save the migration configuration to a JSON file. The save and load options are
useful if you need to exit the tool and resume migration later, or if you would
like to back up your configuration to revert to in the future.""",
    "Load Configuration": """
Load the migration configuration from a JSON file. The save and load options are
useful if you need to exit the tool and resume migration later, or if you would
like to back up your configuration to revert to in the future.""",
    "Verify Configuration": """
Verify that the migration configuration is valid. This refreshes the connections
to Artifactory and Nexus, so if a change in either instance has invalidated the
configuration, the new verification statuses will reflect that.""",
    "Run Migration": """
Execute the configured migration. This will run everything in the configuration,
migrating all settings and artifacts from Nexus to Artifactory. Artifacts will
only be migrated if they don't already exist in Artifactory, so running this
multiple times in a row will only migrate new artifacts each time.""",
    # Initial Setup Menu
    "Nexus Path": """
The local file path to the Nexus instance. For efficiency reasons, this tool
requires file system access to the Nexus server, and so must be run on the same
server, or on a computer with access to the file system where Nexus is
installed, and must be run by a user with read access to the Nexus
installation's directory tree. The correct path to put in this field is a
directory containing the folders: 'conf', 'indexer', 'logs', 'storage',
'timeline', and others.""",
    "Artifactory URL": """
The URL of the Artifactory server. This allows the tool to access the
Artifactory instance via its REST API.""",
    "Artifactory Username": """
The username of an administrative user on the Artifactory server. The tool uses
this user to log in to Artifactory.""",
    "Artifactory Password": """
The password, or an API key, of an administrative user on the Artifactory
server. The tool uses this user to log in to Artifactory.""",
    # Repository Migration Setup Menu
    "Hash All Artifacts": """
If this is checked, all artifacts will have their checksums calculated prior to
migrating. If unchecked, the checksums will be extracted from the Nexus metadata
instead. This option is useful if you believe the Nexus-provided checksums to be
incorrect. Keep in mind that this option can considerably slow the migration
process.""",
    "Edit Repository": """
Press 'e' followed by a number key to edit a repository migration in detail.
Pressing the number key on its own will simply toggle whether or not the
repository will be migrated.""",
    # Edit Repository Menu
    "Repo Name (Nexus)": """
The name of the Nexus repository, prior to migration. This field is not
editable, as it simply shows the name of the repository as it is on the Nexus
server. To change the repository name, modify the "Repo Name (Artifactory)"
field.""",
    "Repo Name (Artifactory)": """
The name that will be given to the repository when it is migrated to
Artifactory. This defaults to the name of the Nexus repository, but can be
changed.""",
    "Migrate This Repo": """
Whether to migrate this repository. If this is unchecked, this repository will
not be migrated.""",
    "Repo Class": """
The repository's class type: local (hosted), remote (proxy), virtual (group), or
shadow (virtual, in Nexus).""",
    "Repo Type": """
The repository's package type (e.g. maven1, maven2, yum, nuget, etc).""",
    "Repo Description": """
The repository's description attribute. Defaults to the Nexus repository's
"display name" attribute.""",
    "Repo Layout": """
The repository's layout. This is automatically set to the default layout for the
repository's package type, but it can be set to another layout if necessary.""",
    "Handles Releases": """
Whether the repository handles release builds.""",
    "Handles Snapshots": """
Whether the repository handles snapshot builds.""",
    "Remote URL": """
The remote URL of the repository to proxy.""",
    # Security Migration Setup Menu
    "Users Migration Setup": """
Set up migration for users. Choose which users are to be migrated and which are
not, and modify those users' details as necessary.""",
    "Groups Migration Setup": """
Set up migration for groups. Choose which groups are to be migrated and which
are not, and modify those groups' details as necessary.""",
    "Permissions Migration Setup": """
Set up migration for permissions. Choose which permissions are to be migrated
and which are not, and modify those permissions' details as necessary.""",
    "LDAP Migration Setup": """
Set up migration for LDAP. Choose whether the LDAP configuration is to be
migrated, and modify its details as necessary.""",
    # Users Migration Setup Menu
    "Default Password": """
The default temporary password assigned to migrated users. Since Nexus hashes
passwords, they cannot be migrated like other data. They must be manually set,
either during configuration, or during the user's first successful login. All
users in the latter category can use this password to log into Artifactory, at
which point they will be prompted to set a new password.""",
    "Edit User": """
Press 'e' followed by a number key to edit a user migration in detail. Pressing
the number key on its own will simply toggle whether or not the user will be
migrated.""",
    # Edit User Menu
    "User Name (Nexus)": """
The name of the Nexus user, prior to migration. This field is not editable, as
it simply shows the name of the user as it is on the Nexus server. To change the
user name, modify the "User Name (Artifactory)" field.""",
    "User Name (Artifactory)": """
The name that will be given to the user when it is migrated to Artifactory. This
defaults to the name of the Nexus user, but can be changed.""",
    "Migrate This User": """
Whether to migrate this user. If this is unchecked, this user will not be
migrated.""",
    "Realm": """
This user's security realm. This is generally either 'internal' or 'ldap'.""",
    "Email Address": """
The email address associated with this user.""",
    "Password": """
The password assigned to this user. Since Nexus hashes passwords, they cannot be
migrated like other data. They must be manually set, either during
configuration, or during the user's first successful login. All users in the
former category can use this value as their password. For security reasons,
admin users are required to set their passwords in this way.""",
    "Groups": """
The groups this user belongs to.""",
    "Is An Administrator": """
Whether the user has administrative privileges. This differs from the Nexus
model, which has special 'application' privileges that grant various
administrative abilities to users; in Artifactory, admin users have all of these
abilities, and all other users do not. For security reasons, passwords must be
explicitly set for admin users, as opposed to using a temporary password.""",
    "Is Enabled": """
Whether this user is enabled. If this is unchecked, this user will be unable to
log in to Artifactory or use their account in any way, until an administrator
re-enabled the account.""",
    # Groups Migration Setup Menu
    "Edit Group": """
Press 'e' followed by a number key to edit a group migration in detail. Pressing
the number key on its own will simply toggle whether or not the group will be
migrated.""",
    # Edit Group Menu
    "Group Name (Nexus)": """
The name of the Nexus role, prior to migration. This field is not editable, as
it simply shows the name of the role as it is on the Nexus server. To change the
group name, modify the "Group Name (Artifactory)" field.""",
    "Group Name (Artifactory)": """
The name that will be given to the group when it is migrated to Artifactory.
This defaults to the name of the Nexus role, but can be changed.""",
    "Migrate This Group": """
Whether to migrate this group. If this is unchecked, this group will not be
migrated.""",
    "Group Description": """
The group's description attribute.""",
    "Auto Join Users": """
Whether newly created users are automatically assigned to this group by
default.""",
    "Permissions": """
The permissions associated with this group.""",
    # Permissions Migration Setup Menu
    "Edit Permission": """
Press 'e' followed by a number key to edit a permission migration in detail.
Pressing the number key on its own will simply toggle whether or not the
permission will be migrated.""",
    # Edit Permission Menu
    "Permission Name (Nexus)": """
The name of the Nexus privilege, prior to migration. This field is not editable,
as it simply shows the name of the privilege as it is on the Nexus server. To
change the permission name, modify the "Permission Name (Artifactory)"
field.""",
    "Permission Name (Artifactory)": """
The name that will be given to the permission when it is migrated to
Artifactory. This defaults to the name of the Nexus permission, but can be
changed.""",
    "Migrate This Permission": """
Whether to migrate this permission. If this is unchecked, this permission will
not be migrated.""",
    "Repository": """
The repository this permission applies to, or ALL.""",
    "Package Type": """
The repository package type this permission applies to, or ALL. Since
Artifactory cannot dynamically apply a permission by package type, if this field
is not ALL, this permission will be applied statically to the appropriate
repositories during migration. This means that any newly created Artifactory
repositories will not have this permission automatically.""",
    "Nexus Regex Patterns": """
The regex patterns for this Nexus privilege. Include and exclude patterns are
generated from this by default, if possible. This field is not editable, and
primarily exists as a reference.""",
    "Include Patterns": """
The include patterns for this permission. This is generated from the Nexus regex
patterns by default, if possible. Otherwise, this field must be set explicitly.
These are Apache Ant-style wildcard patterns (wildcards are ?, *, and **). A
matching path matches at least one include pattern, and exactly zero exclude
patterns.""",
    "Exclude Patterns": """
The exclude patterns for this permission. This is generated from the Nexus regex
patterns by default, if possible. Otherwise, this field must be set explicitly.
These are Apache Ant-style wildcard patterns (wildcards are ?, *, and **). A
matching path matches at least one include pattern, and exactly zero exclude
patterns.""",
    "Reset Patterns": """
Set the include and exclude patterns back to their default values, which are
computed from the Nexus regex patterns.""",
    # Edit Privilege Method Menu
    "Read Permissions": """
Permission to read and download artifacts.""",
    "Create Permissions": """
Permission to create and deploy new artifacts. To update an artifact, both the
create and delete permissions are required, since updating an artifact is simply
deleting the artifact and uploading a new one in its place. The create
permission is also required to add remote artifacts to a cache repository.""",
    "Delete Permissions": """
Permission to delete artifacts. To update an artifact, both the create and
delete permissions are required, since updating an artifact is simply deleting
the artifact and uploading a new one in its place.""",
    "Annotate Permissions": """
Permission to modify the metadata and properties of artifacts.""",
    "Manage Permissions": """
Permission to modify the privilege settings of users for this permission.""",
    # LDAP Migration Setup Menu
    "LDAP Username": """
The username of a privileged LDAP user. These credentials are passed to the LDAP
server to authenticate each LDAP request, unless anonymous authentication is
enabled.""",
    "LDAP Password": """
The password of a privileged LDAP user. These credentials are passed to the LDAP
server to authenticate each LDAP request, unless anonymous authentication is
enabled.""",
    "LDAP Setting Name": """
While Nexus can be configured with a single set of settings for a single LDAP
server, Artifactory supports any number of named sets of settings for any number
of servers. To migrate the settings from Nexus, an LDAP setting name must be
specified.""",
    "LDAP Group Name": """
While Nexus can be configured with a single set of settings for a single LDAP
server, Artifactory supports any number of named sets of settings for any number
of servers. To migrate the settings from Nexus, an LDAP group setting name must
be specified.""",
    "Migrate LDAP": """
Whether to migrate the LDAP settings. If this is unchecked, no LDAP-related
Nexus settings will be migrated."""
}
