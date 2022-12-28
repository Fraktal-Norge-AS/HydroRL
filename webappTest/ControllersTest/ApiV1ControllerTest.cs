using System;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using DKWebapp.Controllers;
using DKWebapp.Models;
using DKWebapp.Models.ApiPoco;
using Microsoft.AspNetCore.Mvc;

namespace DKWebappTest.Controllers
{
    [TestClass]
    public class ApiV1ControllerTest
    {
        private ProjectContext context;
        private ApiV1Controller controller;
        private RunSettings currentSettings;
        private RunSettings previousSettings;

        public ApiV1ControllerTest(){
            context = new ProjectContext{};
            controller = new ApiV1Controller(context);
         
            currentSettings = new RunSettings{
                StepResolution = StepResolution.Day,
                StepFrequency = 2,
                StepsInEpisode = 20
            };
            previousSettings = new RunSettings{
                StepResolution = StepResolution.Day,
                StepFrequency = 2,
                StepsInEpisode = 20
            };
        }
        [TestMethod]
        public void TestValidatePreviousSettings()
        {            
            var error = controller.ValidatePreviousSettings(currentSettings, previousSettings);
            Assert.IsNull(error);            

        }

        [TestMethod]
        public void TestValidatePreviousSettingsThrowsBadRequest(){
            currentSettings.StepFrequency = 3;

            var error = controller.ValidatePreviousSettings(currentSettings, previousSettings);
            Assert.IsNotNull(error);            
        }

        [TestMethod]
        public void TestCalculateTimeSpanDay(){
            var stepResolution = StepResolution.Day;
            int freq = 2;
            int steps = 10;

            TimeSpan actualTimeSpan = controller.calculateTimeSpan(stepResolution, freq, steps);
            TimeSpan expectedTimeSpan = new TimeSpan(freq * steps, 0, 0, 0);

            Assert.AreEqual(expectedTimeSpan, actualTimeSpan);
        }
        [TestMethod]
        public void TestCalculateTimeSpanWeek(){
            var stepResolution = StepResolution.Week;
            int freq = 2;
            int steps = 10;

            TimeSpan actualTimeSpan = controller.calculateTimeSpan(stepResolution, freq, steps);
            TimeSpan expectedTimeSpan = new TimeSpan(freq * steps * 7, 0 ,0 ,0);

            Assert.AreEqual(expectedTimeSpan, actualTimeSpan);
        }
    }
}
