within Dynawo.Electrical.Controls.Machines.Protections;

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

model UVA "Under-Voltage Automaton"
  /* When the monitored voltage goes below a threshold (UMin)
     and does not go back above this threshold within a given time lag
     a tripping order is sent to the generator */

  import Modelica.Constants;

  import Dynawo.Connectors;
  import Dynawo.NonElectrical.Logs.Timeline;
  import Dynawo.NonElectrical.Logs.TimelineKeys;

  public
    parameter Types.AC.VoltageModule UMinPu "Voltage threshold under which the automaton is activated in p.u. (base UNom network)";
    parameter SIunits.Time tLagMeasure "Time-lag before deciding to trip in s";
    parameter SIunits.Time tLagAction "Time-lag due to the actual trip action in s";
    parameter Types.AC.VoltageModule U0Pu  "Initial monitored voltage in p.u. (base UNom network)";

    Connectors.ImPin UPu (value (start = U0Pu)) "Monitored voltage in p.u. (base UNom network)";
    Connectors.BPin switchOffSignal (value (start = false)) "Switch off message for the generator";

  protected
    SIunits.Time tThresholdReached (start = Constants.inf) "Time when the threshold was reached";
    SIunits.Time tDelayReached (start = Constants.inf) "Time when the delay before acting was reached";

  equation
    // Voltage comparison with the minimum accepted value
    when UPu.value <= UMinPu and not(pre(switchOffSignal.value)) then
      tThresholdReached = time;
      Timeline.logEvent1(TimelineKeys.UVAArming);
    elsewhen UPu.value > UMinPu and pre(tThresholdReached) <> Constants.inf and not(pre(switchOffSignal.value)) then
      tThresholdReached = Constants.inf;
      Timeline.logEvent1(TimelineKeys.UVADisarming);
    end when;

    // Delay before tripping the generator
    when time - tThresholdReached >= tLagMeasure then
      tDelayReached = time;
    end when;

    // Delay to account for the information delivery to the generator
    when time - tDelayReached >= tLagAction then
      switchOffSignal.value = true;
      Timeline.logEvent1(TimelineKeys.UVATripped);
    end when;
end UVA;
