from git import Repo


def get_list_of_commits(repo: Repo):
    commits = list(repo.iter_commits())
    commits.reverse()
    commit_docs = []

    for i in range(0, len(commits) - 1):
        older_commit = commits[i]
        newer_commit = commits[i + 1]
        commit_str = newer_commit.message
        diff_str = repo.git.diff(older_commit, newer_commit)
        commit_docs.append({"commit": commit_str, "diff": diff_str})

    return commit_docs
