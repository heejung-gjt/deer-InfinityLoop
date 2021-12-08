import bcrypt
import json
import jwt

from django.test import TestCase, Client

from users.models    import User, Role
from charges.models  import Unit, Type, DiscountOrPenalties
from my_settings     import MY_SECRET_KEY, ALGORITHM


class DiscountViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        Role.objects.bulk_create([Role(id=1, name="관리자"), Role(id=2, name="사용자")])

        user1 = User.objects.create(
            name        ="테스트어드민유저1",
            email       ="test2@server.com",
            phone_number=bcrypt.hashpw("010-1111-2222".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            role_id     =1
        )

        user2 = User.objects.create(
            name        ="테스트커스텀유저1",
            email       ="test1@server.com",
            phone_number=bcrypt.hashpw("010-1111-3333".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            role_id     =2
        )

        self.admin_token = jwt.encode(
            {"user_id": str(user1.id)}, MY_SECRET_KEY, ALGORITHM
        )

        self.customer_token = jwt.encode(
            {"user_id": str(user2.id)}, MY_SECRET_KEY, ALGORITHM
        )

        Type.objects.create(id=1, name="discount")

        Unit.objects.create(id=1, name="%")

        DiscountOrPenalties.objects.create(id=1, number=30, description="주차존 반납", unit_id=1, type_id=1)

    def tearDown(self):
        DiscountOrPenalties.objects.all().delete()
        Unit.objects.all().delete()
        Type.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()

    def test_post_discount_success(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code"       : "D-P-1",
            "number"     : 10,
            "description": "올바른 주차장에 주차했을시 할인율",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "SUCCESS"})

    def test_post_discount_unauthorized_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.customer_token}"}

        data = {
            "code"       : "D-P-1",
            "number"     : 10,
            "description": "올바른 주차장에 주차했을시 할인율",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "UNAUTHORIZED"})

    def test_post_discount_invalid_code(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code"       : "A-P-1",
            "number"     : 10,
            "description": "올바른 주차장에 주차했을시 할인율",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "INVALID_CODE_FORMAT"})

    def test_post_discount_type_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code"       : 9,
            "number"     : 10,
            "description": "올바른 주차장에 주차했을시 할인율",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "TYPE_ERROR"})

    def test_post_discount_key_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {"code": "D-P-3", "description": "올바른 주차장에 주차했을시 할인율", "unit": "%"}

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "KEY_ERROR"})

    def test_post_discount_value_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code"       : "D-P-1",
            "number"     : "",
            "description": "올바른 주차장에 주차했을시 할인율",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/discount", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "VALUE_ERROR"})

    def test_put_discount_success(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "number" : 20,
            "description" : "할인율 변경"
        }

        response = self.client.put(
            "/charges/discount/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"result" : {"discount_rate" : 20, "description" : "할인율 변경"}}
        )

    def test_put_discount_unauthorized(self):
        header = {"HTTP_Authorization": f"Bearer {self.customer_token}"}

        data = {
            "number" : 20,
            "description" : "할인율 변경"
        }

        response = self.client.put(
            "/charges/discount/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"message": "UNAUTHORIZED"}
        )
    
    def test_put_discount_does_not_exist(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "number" : 20,
            "description" : "할인율 변경"
        }

        response = self.client.put(
            "/charges/discount/2",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"message": "DISCOUNT_DOES_NOT_EXIST"}
        )

    def test_put_discount_key_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "description" : "할인율 변경"
        }

        response = self.client.put(
            "/charges/discount/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"message": "KEY_ERROR"}
        )


class PenaltyViewTest1(TestCase):
    def setUp(self):
        self.client = Client()

        Role.objects.create(id=1, name="관리자")
        Role.objects.create(id=2, name="사용자")

        user1 = User.objects.create(
            email="abc@gmail.com",
            phone_number = bcrypt.hashpw("010-2345-3544".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            name="관리자",
            role_id=1,
        )

        self.admin_token = jwt.encode(
            {"user_id": str(user1.id)}, MY_SECRET_KEY, ALGORITHM
        )

        user2 = User.objects.create(
            id="bf7d24f136804c027e35fa9a72cc8b67",
            email="abc3@gmail.com",
            phone_number = bcrypt.hashpw("010-2345-3544".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            name="유저1",
            role_id=2,
        )

        self.customer_token = jwt.encode(
            {"user_id": str(user2.id)}, MY_SECRET_KEY, ALGORITHM
        )

        Type.objects.create(id=1, name="penalty")

        Unit.objects.create(id=1, name="원")

        DiscountOrPenalties.objects.create(id=1, number=6000, description="반납 금지 지역 반납", unit_id=1, type_id=1)

    def tearDown(self):
        DiscountOrPenalties.objects.all().delete()
        Unit.objects.all().delete()
        Type.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()

    def test_put_penalty_success(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "number" : 6000,
            "description" : "반납 금지 지역 반납"
        }

        response = self.client.put(
            "/charges/penalty/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"result" : {"penalty" : 6000,
                "description" : "반납 금지 지역 반납"}}
        )

    def test_put_penalty_unauthorized(self):
        header = {"HTTP_Authorization": f"Bearer {self.customer_token}"}

        data = {
            "number" : 6000,
            "description" : "반납 금지 지역 반납"
        }

        response = self.client.put(
            "/charges/penalty/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"message": "UNAUTHORIZED"}
        )
    
    def test_put_penalty_does_not_exist(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "number" : 6000,
            "description" : "반납 금지 지역 반납"
        }

        response = self.client.put(
            "/charges/penalty/2",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"message": "PENALTY_DOES_NOT_EXIST"}
        )

    def test_put_penalty_key_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "description" : "반납 금지 지역 반납"
        }

        response = self.client.put(
            "/charges/penalty/1",
            json.dumps(data),
            content_type="application/json",
            **header
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"message": "KEY_ERROR"}
        )


class PenaltyViewTest2(TestCase):
    def setUp(self):
        self.client = Client()

        Unit.objects.create(id=1, name="원")

        Type.objects.create(id=2, name="PENALTY")

        Role.objects.bulk_create([Role(id=1, name="관리자"), Role(id=2, name="사용자")])

        user1 = User.objects.create(
            name        ="테스트어드민유저1",
            email       ="test2@server.com",
            phone_number=bcrypt.hashpw("010-1111-2222".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            role_id     =1
        )

        user2 = User.objects.create(
            name        ="테스트커스텀유저1",
            email       ="test1@server.com",
            phone_number=bcrypt.hashpw("010-1111-2222".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            role_id     =2
        )

        self.admin_token = jwt.encode(
            {"user_id": str(user1.id)}, MY_SECRET_KEY, ALGORITHM
        )

        self.customer_token = jwt.encode(
            {"user_id": str(user2.id)}, MY_SECRET_KEY, ALGORITHM
        )

    def tearDown(self):
        DiscountOrPenalties.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()
        Type.objects.all().delete()
        Unit.objects.all().delete()

    def test_post_penalty_success(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code": "P-P-1",
            "number": 1000,
            "description": "올바르지 않은 주차구역에 주차했을시 벌금금액",
            "unit"       : "원"
        }

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "SUCCESS"})

    def test_post_penalty_unauthorized_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.customer_token}"}

        data = {
            "code": "P-P-1",
            "number": 1000,
            "description": "올바르지 않은 주차구역에 주차했을시 벌금금액",
            "unit"       : "원"
        }

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "UNAUTHORIZED"})

    def test_post_penalty_invalid_code(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code": "O-P-1",
            "number": 1000,
            "description": "올바르지 않은 주차구역에 주차했을시 벌금금액",
            "unit"       : "원"
        }

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "INVALID_CODE_FORMAT"})

    def test_post_penalty_type_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code": 1,
            "number": 10,
            "description": "올바르지 않은 주차구역에 주차했을시 벌금금액",
            "unit"       : "%"
        }

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "TYPE_ERROR"})

    def test_post_penalty_key_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {"code": "P-P-3"}

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "KEY_ERROR"})

    def test_post_penalty_value_error(self):
        header = {"HTTP_Authorization": f"Bearer {self.admin_token}"}

        data = {
            "code"       : "P-P-3",
            "number"     : "",
            "description": "올바르지 않은 주차구역에 주차했을시 벌금금액",
            "unit"       : "원"
        }

        response = self.client.post(
            "/charges/penalty", json.dumps(data), content_type="application/json", **header
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "VALUE_ERROR"})
