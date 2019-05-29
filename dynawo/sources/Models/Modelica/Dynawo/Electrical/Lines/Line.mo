within Dynawo.Electrical.Lines;

/*
* Copyright (c) 2015-2019, RTE (http://www.rte-france.com)
* See AUTHORS.txt
* All rights reserved.
* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, you can obtain one at http://mozilla.org/MPL/2.0/.
* SPDX-License-Identifier: MPL-2.0
*
* This file is part of Dynawo, an hybrid C++/Modelica open source time domain simulation tool for power systems.
*/

model Line "AC power line - PI model"

/*
  Equivalent circuit and conventions:

               I1                  I2
   (terminal1) -->-------R+jX-------<-- (terminal2)
                    |           |
                  G+jB         G+jB
                    |           |
                   ---         ---
*/

  import Dynawo.Connectors;
  import Dynawo.Electrical.Controls.Basics.SwitchOff;

  extends SwitchOff.SwitchOffLine;

  Connectors.ACPower terminal1;
  Connectors.ACPower terminal2;

  parameter Types.PerUnit RPu "Resistance in p.u (base SnRef)";
  parameter Types.PerUnit XPu "Reactance in p.u (base SnRef)";
  parameter Types.PerUnit GPu "Half-conductance in p.u (base SnRef)";
  parameter Types.PerUnit BPu "Half-susceptance in p.u (base SnRef)";

protected
  parameter Types.ComplexImpedancePu ZPu (re = RPu, im = XPu) "Line impedance";
  parameter Types.ComplexAdmittancePu YPu (re = GPu, im = BPu) "Line half-admittance";

equation

  if (running.value) then
    ZPu * (terminal2.i - YPu * terminal2.V) = terminal2.V - terminal1.V;
    ZPu * (terminal1.i - YPu * terminal1.V) = terminal1.V - terminal2.V;
  else
    terminal1.i = Complex (0);
    terminal2.i = Complex (0);
  end if;

end Line;
