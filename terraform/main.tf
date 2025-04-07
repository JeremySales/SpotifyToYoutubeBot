provider "azurerm" {
  features {}

  # Add your subscription_id here
  subscription_id = var.subscription_id

  # Optionally, you can also set the tenant_id and client_id (service principal) if you're using one
  # tenant_id     = var.tenant_id
  # client_id     = var.client_id
  # client_secret = var.client_secret
}

locals {
  resource_group_name = "bot-bois-only-rg"
}

data "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
}
resource "azurerm_app_service_plan" "plan" {
  name                = "spotifyyt-plan"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Free"
    size = "F1"
  }
}

# Fetch existing ACR details using data source
data "azurerm_container_registry" "existing_acr" {
  name                = "basicbotboiacr"
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_app_service" "app" {
  name                = "spotify-yt-discord-bot"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.plan.id

  app_settings = {
    "DOCKER_REGISTRY_SERVER_URL"      = "https://${data.azurerm_container_registry.existing_acr.login_server}"
    "DOCKER_REGISTRY_SERVER_USERNAME" = data.azurerm_container_registry.existing_acr.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD" = data.azurerm_container_registry.existing_acr.admin_password
    "WEBSITES_PORT"                   = "80"
    "DISCORD_BOT_TOKEN"               = var.discord_bot_token
    "SPOTIFY_CLIENT_ID"               = var.spotify_client_id
    "SPOTIFY_CLIENT_SECRET"           = var.spotify_client_secret
    "OWNER_ID"                        = var.owner_id
  }

  site_config {
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.existing_acr.login_server}/spotify-youtube-bot:latest"
    ip_restriction {
      action    = "Deny"
      priority  = 100
      name      = "Deny All"
      ip_address = "0.0.0.0/0"
    }
  }
}
