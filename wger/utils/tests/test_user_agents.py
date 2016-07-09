# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License


from wger.core.tests.base_testcase import WorkoutManagerTestCase

from wger.utils import user_agents


class AmazonUserAgentTestCase(WorkoutManagerTestCase):
    '''
    Tests the amazon WebApp user agent detector
    '''

    def test_user_agent_3rd_generation(self):
        '''
        Tests 3rd generation user agents
        '''

        agent = "Mozilla/5.0 (Linux; Android 4.2.2; <device> Build/<build>) AppleWebKit/ "\
                "<webkit> (KHTML, like Gecko) Chrome/<chrome> Mobile Safari/<safari> "\
                "AmazonWebAppPlatform/<version> "
        self.assertTrue(user_agents.is_amazon_webview(agent))

    def test_user_agent_2nd_generation(self):
        '''
        Tests 2nd generation user agents
        '''

        agent = "Mozilla/5.0 (Linux; Android 4.0.3; <device> Build/<build>) AppleWebKit/<webkit>" \
                "(KHTML, like Gecko) Chrome/<chrome> Mobile Safari/<safari> AmazonWebAppPlatform"\
                "/<version>"
        self.assertTrue(user_agents.is_amazon_webview(agent))

    def test_user_agent_1st_generation(self):
        '''
        Tests 1st generation user agents
        '''

        agent = "Mozilla/5.0 (Linux; U; Android 2.3.4; <locale>; Kindle Fire Build/GINGERBREAD) "\
                "AppleWebKit/<webkit> (KHTML, like Gecko) Version/4.0 Safari/<safari> "\
                "AmazonWebAppPlatform/<version> "
        self.assertTrue(user_agents.is_amazon_webview(agent))

    def test_user_agent_generic_android(self):
        '''
        Tests generic android, from amazon app store
        '''

        agent = "Mozilla/5.0 (Linux; U; Android <version>; <locale>; Build/<build>) AppleWebKit/"\
                "<webkit> (KHTML, like Gecko) Version/4.0 Safari/<safari> AmazonWebAppPlatform/"\
                "<version>"
        self.assertTrue(user_agents.is_amazon_webview(agent))

    def test_user_agent_firefox(self):
        '''
        Tests vanilla firefox user agent
        '''

        agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"
        self.assertFalse(user_agents.is_amazon_webview(agent))

        agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"
        self.assertFalse(user_agents.is_amazon_webview(agent))

    def test_user_agent_chrome(self):
        '''
        Tests vanilla chrome user agent
        '''

        agent = "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
                "Chrome/32.0.1667.0 Safari/537.36"
        self.assertFalse(user_agents.is_amazon_webview(agent))

        agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like "\
                "Gecko) Chrome/32.0.1664.3 Safari/537.36"
        self.assertFalse(user_agents.is_amazon_webview(agent))


class AndroidUserAgentTestCase(WorkoutManagerTestCase):
    '''
    Tests the android WebApp user agent detector

    https://developers.google.com/chrome/mobile/docs/webview/overview
    '''

    def test_user_agent_old_ua(self):
        '''
        Tests the old webview user agent
        '''

        agent = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 "\
                "(KHTML, like Gecko) Version/4.0 Safari/534.30 WgerAndroidWebApp"
        self.assertTrue(user_agents.is_android_webview(agent))

    def test_user_agent_new_ua(self):
        '''
        Tests the old webview user agent
        '''

        agent = "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/BuildID) AppleWebKit/537.36 "\
                "(KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 "\
                "WgerAndroidWebApp"
        self.assertTrue(user_agents.is_android_webview(agent))

    def test_user_agent_firefox(self):
        '''
        Tests vanilla firefox user agent
        '''

        agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"
        self.assertFalse(user_agents.is_android_webview(agent))

        agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"
        self.assertFalse(user_agents.is_android_webview(agent))

    def test_user_agent_chrome(self):
        '''
        Tests vanilla chrome user agent
        '''

        agent = "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
                "Chrome/32.0.1667.0 Safari/537.36"
        self.assertFalse(user_agents.is_android_webview(agent))

        agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like "\
                "Gecko) Chrome/32.0.1664.3 Safari/537.36"
        self.assertFalse(user_agents.is_android_webview(agent))
