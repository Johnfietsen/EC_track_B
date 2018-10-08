/*
* Copyright (C) 2017 Vrije Universiteit Amsterdam
*
* Licensed under the Apache License, Version 2.0 (the "License");
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
* Author: Elte Hupkes
* Date: May 3, 2015
*
*/

#include <gazebo/sensors/sensors.hh>

#include <revolve/gazebo/motors/MotorFactory.h>
#include <revolve/gazebo/sensors/SensorFactory.h>
#include <revolve/gazebo/brain/NeuralNetwork.h>
#include <revolve/gazebo/brain/RLPower.h>

#include "RobotController.h"

namespace gz = gazebo;

using namespace revolve::gazebo;

/////////////////////////////////////////////////
/// Default actuation time is given and this will be overwritten by the plugin
/// config in Load.
RobotController::RobotController()
    : actuationTime_(0)
{
}

/////////////////////////////////////////////////
RobotController::~RobotController()
{
  this->node_.reset();
  this->world_.reset();
  this->motorFactory_.reset();
  this->sensorFactory_.reset();
}

/////////////////////////////////////////////////
void RobotController::Load(
    ::gazebo::physics::ModelPtr _parent,
    sdf::ElementPtr _sdf)
{
  // Store the pointer to the model / world
  this->model_ = _parent;
  this->world_ = _parent->GetWorld();
  this->initTime_ = this->world_->GetSimTime().Double();

  // Create transport node
  this->node_.reset(new gz::transport::Node());
  this->node_->Init();

  // Subscribe to robot battery state updater
  this->batterySetSub_ = this->node_->Subscribe(
      "~/battery_level/request",
      &RobotController::UpdateBattery,
      this);
  this->batterySetPub_ = this->node_->Advertise< gz::msgs::Response >(
      "~/battery_level/response");

  if (not _sdf->HasElement("rv:robot_config"))
  {
    std::cerr
        << "No `rv:robot_config` element found, controller not initialized."
        << std::endl;
    return;
  }

  auto settings = _sdf->GetElement("rv:robot_config");

  if (settings->HasElement("rv:update_rate"))
  {
    auto updateRate = settings->GetElement("rv:update_rate")->Get< double >();
    this->actuationTime_ = 1.0 / updateRate;
  }

  // Load motors
  this->motorFactory_ = this->MotorFactory(_parent);
  this->LoadMotors(settings);

  // Load sensors
  this->sensorFactory_ = this->SensorFactory(_parent);
  this->LoadSensors(settings);

  // Load brain, this needs to be done after the motors and sensors so they
  // can potentially be reordered.
  this->LoadBrain(settings);

  // Call the battery loader
  this->LoadBattery(settings);

  // Call startup function which decides on actuation
  this->Startup(_parent, _sdf);
}

/////////////////////////////////////////////////
void RobotController::UpdateBattery(ConstRequestPtr &_request)
{
  if (_request->data() not_eq this->model_->GetName() and
      _request->data() not_eq this->model_->GetScopedName())
  {
    return;
  }

  gz::msgs::Response resp;
  resp.set_id(_request->id());
  resp.set_request(_request->request());

  if (_request->request() == "set_battery_level")
  {
    resp.set_response("success");
    this->SetBatteryLevel(_request->dbl_data());
  }
  else
  {
    std::stringstream ss;
    ss << this->BatteryLevel();
    resp.set_response(ss.str());
  }

  batterySetPub_->Publish(resp);
}

/////////////////////////////////////////////////
void RobotController::LoadMotors(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:motor"))
  {
    return;
  }

  auto motor = _sdf->GetElement("rv:motor");
  while (motor)
  {
    auto motorObj = this->motorFactory_->Create(motor);
    motors_.push_back(motorObj);
    motor = motor->GetNextElement("rv:motor");
  }
}

/////////////////////////////////////////////////
void RobotController::LoadSensors(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:sensor"))
  {
    return;
  }

  auto sensor = _sdf->GetElement("rv:sensor");
  while (sensor)
  {
    auto sensorObj = this->sensorFactory_->Create(sensor);
    sensors_.push_back(sensorObj);
    sensor = sensor->GetNextElement("rv:sensor");
  }
}

/////////////////////////////////////////////////
MotorFactoryPtr RobotController::MotorFactory(
    ::gazebo::physics::ModelPtr _model)
{
  return MotorFactoryPtr(new class MotorFactory(_model));
}

/////////////////////////////////////////////////
SensorFactoryPtr RobotController::SensorFactory(
    ::gazebo::physics::ModelPtr _model)
{
  return SensorFactoryPtr(new class SensorFactory(_model));
}

/////////////////////////////////////////////////
void RobotController::LoadBrain(const sdf::ElementPtr _sdf)
{
  if (not _sdf->HasElement("rv:brain"))
  {
    std::cerr << "No robot brain detected, this is probably an error."
              << std::endl;
    return;
  }

  auto brain = _sdf->GetElement("rv:brain");
  brain_.reset(new RLPower(this->model_, brain, motors_, sensors_));
}

/////////////////////////////////////////////////
/// Default startup, bind to CheckUpdate
void RobotController::Startup(
    ::gazebo::physics::ModelPtr /*_parent*/,
    sdf::ElementPtr /*_sdf*/)
{
  this->updateConnection_ = gz::event::Events::ConnectWorldUpdateBegin(
      boost::bind(&RobotController::CheckUpdate, this, _1));
}

/////////////////////////////////////////////////
void RobotController::CheckUpdate(const ::gazebo::common::UpdateInfo _info)
{
  auto diff = _info.simTime - lastActuationTime_;

  if (diff.Double() > actuationTime_)
  {
    this->DoUpdate(_info);
    lastActuationTime_ = _info.simTime;
  }
}

/////////////////////////////////////////////////
/// Default update function simply tells the brain to perform an update
void RobotController::DoUpdate(const ::gazebo::common::UpdateInfo _info)
{
  auto currentTime = _info.simTime.Double() - initTime_;

  brain_->Update(motors_, sensors_, currentTime, actuationTime_);
}

/////////////////////////////////////////////////
void RobotController::LoadBattery(const sdf::ElementPtr _sdf)
{
  if (_sdf->HasElement("rv:battery"))
  {
    this->batteryElem_ = _sdf->GetElement("rv:battery");
  }
}

/////////////////////////////////////////////////
double RobotController::BatteryLevel()
{
  if (not batteryElem_ or not batteryElem_->HasElement("rv:level"))
  {
    return 0.0;
  }

  return batteryElem_->GetElement("rv:level")->Get< double >();
}

/////////////////////////////////////////////////
void RobotController::SetBatteryLevel(double _level)
{
  if (batteryElem_ and batteryElem_->HasElement("rv:level"))
  {
    batteryElem_->GetElement("rv:level")->Set(_level);
  }
}
