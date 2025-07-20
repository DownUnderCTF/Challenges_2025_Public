require 'redis'
require 'json'

class MainController < ApplicationController
  include ActionController::HttpAuthentication::Basic::ControllerMethods

  before_action :authenticate

  def lol_what_could_go_wrong
    if !@authenticated
      request_http_basic_authentication
      return
    end

    config_file = params[:config]
    config_hash = JSON.load_file(config_file)
    config_hash["type"].constantize.new(config_hash["arg"])
    render json: {success: true}
  end

  def req_params
    params.require(:config)
  end

  def authenticate
    authenticate_with_http_basic do |u, p|
      redis = Redis.new(host: "127.0.0.1", port: 6379)
      at = redis.get(u)
      @authenticated = at === p
    end
  end
end