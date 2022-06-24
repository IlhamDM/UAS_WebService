//6D 18090122 Dimas Ilham Mardiyanto
//6D 18090139 Alfan Nur Rabbani
package com.poltekharber.seeaspal;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import androidx.annotation.Nullable;

public class DBHelper extends SQLiteOpenHelper {
    public static final String database_name = "db_login";
    public static final String table_name = "table_login";

    public static final String row_id = "_id";
    public static final String row_name = "Name";
    public static final String row_username = "Username";
    public static final String row_password = "Password";

//    private SQLiteDatabase db;

    public DBHelper(Context context) {
        super(context, database_name, null, 2);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String query = "CREATE TABLE " + table_name + "(" + row_id + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + row_name + " TEXT," + row_username + " TEXT," + row_password + " TEXT)";
        db.execSQL(query);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int i, int i1) {
        db.execSQL(("DROP TABLE IF EXISTS " + table_name));
        onCreate(db);
    }

    public void insertData(ContentValues values){
        SQLiteDatabase db = this.getWritableDatabase();
        db.insert(table_name, null, values);
    }

    public boolean checkUser(String username, String password){
        String[] coloumn = {row_id};
        SQLiteDatabase db = this.getReadableDatabase();
        String selection = row_username + "=?" + " and " + row_password + "=?";
        String[] selectionArgs = {username,password};
        Cursor cursor = db.query(table_name, coloumn, selection, selectionArgs, null, null, null);
        int count = cursor.getCount();
        cursor.close();
        db.close();

        if(count>0)
            return true;
        else
            return false;

    }
}

