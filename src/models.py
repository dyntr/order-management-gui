import hashlib
from src.db_operations import get_connection, fetch_all, execute_query

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class User:
    def __init__(self,user_id=None,username=None,password_hash=None,
                 email=None,is_active="Aktivní",created_at=None):
        self.user_id=user_id
        self.username=username
        self.password_hash=password_hash
        self.email=email
        self.is_active=is_active
        self.created_at=created_at

    def save(self):
        c=get_connection()
        k=c.cursor()
        try:
            if self.user_id is None:
                k.execute("""
                    INSERT INTO Users (Username,PasswordHash,Email,IsActive,CreatedAt)
                    VALUES (%s,%s,%s,%s,NOW())
                """,(self.username,self.password_hash,self.email,self.is_active))
                self.user_id=k.lastrowid
            else:
                k.execute("""
                    UPDATE Users
                    SET Username=%s,PasswordHash=%s,Email=%s,IsActive=%s
                    WHERE UserID=%s
                """,(self.username,self.password_hash,self.email,self.is_active,self.user_id))
            c.commit()
        except:
            c.rollback()
            raise
        finally:
            k.close()
            c.close()

    def delete(self):
        if self.user_id:
            execute_query("DELETE FROM Users WHERE UserID=%s",(self.user_id,))
            self.user_id=None

    @staticmethod
    def find_by_username_and_password(u,p):
        h=hash_password(p)
        r=fetch_all("SELECT * FROM Users WHERE Username=%s AND PasswordHash=%s",(u,h))
        if not r:return None
        x=r[0]
        if x[4]!="Aktivní":
            return None
        return User(x[0],x[1],x[2],x[3],x[4],x[5])

    @staticmethod
    def find_by_id(i):
        r=fetch_all("SELECT * FROM Users WHERE UserID=%s",(i,))
        if not r:return None
        x=r[0]
        return User(x[0],x[1],x[2],x[3],x[4],x[5])

class Order:
    def __init__(self, order_id=None, user_id=None, order_date=None, total_amount=0.0):
        self.order_id=order_id
        self.user_id=user_id
        self.order_date=order_date
        self.total_amount=total_amount
        self.details=[]

    def save(self):
        c=get_connection()
        cur=c.cursor()
        try:
            if self.order_id is None:
                cur.execute("""
                    INSERT INTO Orders (UserID,OrderDate,TotalAmount)
                    VALUES (%s,NOW(),%s)
                """,(self.user_id,self.total_amount))
                self.order_id=cur.lastrowid
            else:
                cur.execute("""
                    UPDATE Orders
                    SET UserID=%s,TotalAmount=%s
                    WHERE OrderID=%s
                """,(self.user_id,self.total_amount,self.order_id))
            cur.execute("DELETE FROM OrderDetails WHERE OrderID=%s",(self.order_id,))
            for d in self.details:
                cur.execute("SELECT Stock FROM Products WHERE ProductID=%s",(d.product_id,))
                row=cur.fetchone()
                if not row: raise Exception("Produkt neexistuje.")
                skl=row[0]
                if skl<d.quantity: raise Exception("Nedostatek na skladě.")
                cur.execute("""
                    INSERT INTO OrderDetails (OrderID,ProductID,Quantity,PricePerUnit)
                    VALUES (%s,%s,%s,%s)
                """,(self.order_id,d.product_id,d.quantity,d.price_per_unit))
                cur.execute("UPDATE Products SET Stock=Stock - %s WHERE ProductID=%s",(d.quantity,d.product_id))
            c.commit()
        except:
            c.rollback()
            raise
        finally:
            cur.close()
            c.close()

class OrderDetail:
    def __init__(self,order_detail_id=None,order_id=None,product_id=None,
                 quantity=1,price_per_unit=0.0):
        self.order_detail_id=order_detail_id
        self.order_id=order_id
        self.product_id=product_id
        self.quantity=quantity
        self.price_per_unit=price_per_unit
