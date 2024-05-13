within Dynawo.Electrical.Controls.IEC.BaseControls.Auxiliaries;

/*
* Copyright (c) 2024, RTE (http://www.rte-france.com)
* See AUTHORS.txt
* All rights reserved.
* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, you can obtain one at http://mozilla.org/MPL/2.0/.
* SPDX-License-Identifier: MPL-2.0
*
* This file is part of Dynawo, an hybrid C++/Modelica open source suite of simulation tools for power systems.
*/

model UfMeasurement "Measurement module for grid protection (IEC N°61400-27-1:2015)"

  //Nominal parameters
  parameter Types.Time tS "Integration time step in s";

  //Uf measurement parameters
  parameter Types.AngularVelocityPu DfMaxPu "Maximum frequency ramp rate in pu/s (base omegaNom)" annotation(
    Dialog(tab = "UfMeasurement"));
  parameter Types.Time tfFilt "Filter time constant for frequency measurement in s" annotation(
    Dialog(tab = "UfMeasurement"));
  parameter Types.Time tUFilt "Filter time constant for voltage measurement in s" annotation(
    Dialog(tab = "UfMeasurement"));

  //Input variables
  Modelica.Blocks.Interfaces.RealInput omegaRefPu(start = Dynawo.Electrical.SystemBase.omegaRef0Pu) "Grid angular frequency in pu (base omegaNom)" annotation(
    Placement(visible = true, transformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-142, -790}, extent = {{-42, -42}, {42, 42}}, rotation = 0)));
  Modelica.ComplexBlocks.Interfaces.ComplexInput uWTPu(re(start = u0Pu.re), im(start = u0Pu.im)) "Complex voltage at grid terminal in pu (base UNom)" annotation(
    Placement(visible = true, transformation(origin = {-120, 48}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-142, 814}, extent = {{-42, -42}, {42, 42}}, rotation = 0)));

  //Output variables
  Modelica.Blocks.Interfaces.RealOutput omegaGenPu(start = Dynawo.Electrical.SystemBase.omegaRef0Pu) "Filtered grid angular frequency in pu (base omegaNom)" annotation(
    Placement(visible = true, transformation(origin = {160, 34}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {142, -790}, extent = {{-42, -42}, {42, 42}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput UWTFiltPu(start = U0Pu) "Filtered voltage amplitude at grid terminal in pu (base UNom)" annotation(
    Placement(visible = true, transformation(origin = {160, 74}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {143, 811}, extent = {{-43, -43}, {43, 43}}, rotation = 0)));

  Modelica.ComplexBlocks.ComplexMath.ComplexToPolar complexToPolar annotation(
    Placement(visible = true, transformation(origin = {-72, 46}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.Derivative derivative(T = tfFilt / 20,k = 1 / SystemBase.omegaNom, x_start = UPhase0, y_start = 0) annotation(
    Placement(visible = true, transformation(origin = {-18, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Add add annotation(
    Placement(visible = true, transformation(origin = {134, 34}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Dynawo.NonElectrical.Blocks.NonLinear.RampLimiter rampLimiter(DuMax = DfMaxPu, DuMin = -DfMaxPu, Y0 = 0, tS = tS)  annotation(
    Placement(visible = true, transformation(origin = {20, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.FirstOrder firstOrder(T = tfFilt, y_start = 0)  annotation(
    Placement(visible = true, transformation(origin = {56, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.FirstOrder firstOrder1(T = tUFilt, y_start = U0Pu)  annotation(
    Placement(visible = true, transformation(origin = {-18, 74}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));

  //Initial parameters
  parameter Dynawo.Types.VoltageModulePu U0Pu "Initial voltage amplitude at grid terminal in pu (base UNom)" annotation(
    Dialog(tab = "Operating point"));
  parameter Dynawo.Types.ComplexVoltagePu u0Pu "Initial complex voltage at grid terminal in pu (base UNom)" annotation(
    Dialog(group = "Initialization"));
  parameter Types.Angle UPhase0 "Initial voltage angle at grid terminal in rad" annotation(
    Dialog(tab = "Operating point"));

equation
  connect(uWTPu, complexToPolar.u) annotation(
    Line(points = {{-120, 48}, {-102, 48}, {-102, 46}, {-84, 46}}, color = {85, 170, 255}));
  connect(omegaRefPu, add.u2) annotation(
    Line(points = {{-120, 0}, {116, 0}, {116, 28}, {122, 28}}, color = {0, 0, 127}));
  connect(add.y, omegaGenPu) annotation(
    Line(points = {{146, 34}, {160, 34}}, color = {0, 0, 127}));
  connect(complexToPolar.phi, derivative.u) annotation(
    Line(points = {{-60, 40}, {-30, 40}}, color = {0, 0, 127}));
  connect(firstOrder.y, add.u1) annotation(
    Line(points = {{67, 40}, {122, 40}}, color = {0, 0, 127}));
  connect(firstOrder1.y, UWTFiltPu) annotation(
    Line(points = {{-6, 74}, {160, 74}}, color = {0, 0, 127}));
  connect(complexToPolar.len, firstOrder1.u) annotation(
    Line(points = {{-60, 52}, {-40, 52}, {-40, 74}, {-30, 74}}, color = {0, 0, 127}));
  connect(derivative.y, rampLimiter.u) annotation(
    Line(points = {{-6, 40}, {8, 40}}, color = {0, 0, 127}));
  connect(rampLimiter.y, firstOrder.u) annotation(
    Line(points = {{31, 40}, {44, 40}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-100, -100}, {150, 100}})),
    Icon(coordinateSystem(extent = {{-100, -900}, {100, 900}}), graphics = {Rectangle(fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-100, 900}, {100, -900}}), Text(origin = {-1, 24}, rotation = -90, extent = {{-441, 82}, {441, -82}}, textString = "Uf measurement")}));
end UfMeasurement;
