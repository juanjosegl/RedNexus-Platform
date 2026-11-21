locals {
  # Check obligatorio de cada repo (nombre del job de su CI)
  repos = {
    Backend  = { name = "RedNexus-Backend", check = "build-test" }
    Frontend = { name = "RedNexus-Frontend", check = "build-test" }
    Platform = { name = "RedNexus-Platform", check = "validate" }
  }

  # Flujo de CONTRIBUTING.md: a developer se entra con squash desde ramas temporales;
  # las promociones developer -> test -> main usan merge commit.
  branches = {
    developer = "squash"
    test      = "merge"
    main      = "merge"
  }

  rulesets = merge([
    for repo_key, repo in local.repos : {
      for branch, method in local.branches : "${repo_key}/${branch}" => {
        repository   = repo.name
        branch       = branch
        merge_method = method
        check        = repo.check
      }
    }
  ]...)

  github_actions_app_id = 15368
  admin_role_id         = 5 # rol "Admin" del repositorio
}

resource "github_repository_ruleset" "rama" {
  for_each = local.rulesets

  name        = "${each.value.branch}: solo por PR"
  repository  = each.value.repository
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/heads/${each.value.branch}"]
      exclude = []
    }
  }

  # El administrador puede fusionar sin aprobación, pero siempre por PR
  bypass_actors {
    actor_id    = local.admin_role_id
    actor_type  = "RepositoryRole"
    bypass_mode = "pull_request"
  }

  rules {
    deletion         = true
    non_fast_forward = true

    pull_request {
      required_approving_review_count   = 1
      dismiss_stale_reviews_on_push     = true
      require_code_owner_review         = false
      require_last_push_approval        = false
      required_review_thread_resolution = false
      allowed_merge_methods             = [each.value.merge_method]
    }

    required_status_checks {
      strict_required_status_checks_policy = false
      required_check {
        context        = each.value.check
        integration_id = local.github_actions_app_id
      }
    }
  }
}
