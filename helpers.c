#include <inttypes.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include "helpers.h"

 #define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })
 #define max(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a > _b ? _a : _b; })

int walkable_tile_types[] = {2, 3};
int resource_tile_types[] = {4, 5, 6, 7};
int adjacentPositionOffsetList[8][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}};
int width = 200;
int height = 200;

struct tile **tiles;
struct vec2d generatorPos;
struct rect generatorRect;


extern int explorable(int x, int y) {
    if(x < 0) {
        return 0;
    }
    if(x >= width) {
        return 0;
    }
    if(y < 0) {
        return 0;
    }
    if(y >= height) {
        return 0;
    }
    if (tiles[y][x].solid == 1) {
        return 0;
    }
    return 1;
}


extern int inMap(double x, double y) {
    x = (int)x;
    y = (int)y;
    if(x < 0) {
        return 0;
    }
    if(x >= width) {
        return 0;
    }
    if(y < 0) {
        return 0;
    }
    if(y >= height) {
        return 0;
    }
    return 1;
}

extern int init(int newWidth, int newHeight) {
    int x, y;
    // Make a pointer for each global variable, so we can modify them.
    int * pWidth = &width;
    int * pHeight = &height;

    // Give the pointers of the global variables their value. This modifies the global variables!
    *pWidth = newWidth;
    *pHeight = newHeight;
    
    // Allocate memory for the tiles array.
    tiles = malloc(sizeof(struct tile*)*height);
    // Make rows in the tiles array.
    for(y=0; y<height + 1; y++) {
        tiles[y] = malloc(sizeof(struct tile) * width);
        for (x=0; x<width; x++) {
            tiles[y][x].x = x;
            tiles[y][x].y = y;
            tiles[y][x].right = x + 1;
            tiles[y][x].top = y + 1;
            tiles[y][x].solid = 0;
            tiles[y][x].gCost = 0;
            tiles[y][x].hCost = 0;
            tiles[y][x].fCost = 0;
            tiles[y][x].direction = 0;
            tiles[y][x].explored = 0;
            tiles[y][x].initiated = 0;
            tiles[y][x].neighborGCost = 0;
        }
    }
}

extern void setTile(int x, int y, int type) {
    tiles[y][x].type = type;

    if (intInArray(tiles[y][x].type, walkable_tile_types, 2)) {
        tiles[y][x].solid = 0;
    }
    else {
        tiles[y][x].solid = 1;
    }
}

int getTileSolidity(int x, int y) {
    return tiles[y][x].solid;
}

struct vec2d getVectorFromPoints(double firstX, double firstY, double secondX, double secondY) {
    struct vec2d distance;
    struct vec2d direction;
    struct vec2d vector;
    distance.x = secondX - firstX;
    distance.y = secondY - firstY;
    double norm = sqrt(pow(distance.x, 2) + pow(distance.y, 2));
    if (distance.x != 0 || distance.y != 0) {
        direction.x = distance.x / norm;
        direction.y = distance.y / norm;
        vector.x = direction.x * sqrt(2);
        vector.y = direction.y * sqrt(2);
    }
    else {
        vector.x = 0;
        vector.y = 0;
    }
    return vector;
}

double getVectorMagnitude(struct vec2d vector) {
    return sqrt(pow(vector.x, 2) + pow(vector.y, 2));
}

struct vec2d getNormalized(struct vec2d vector) {
    // We are using the inverse here so we can avoid division by zero.
    double magnitudeInverse = 1 / getVectorMagnitude(vector);
    vector.x *= magnitudeInverse;
    vector.y *= magnitudeInverse;
    return vector;
}

extern double getDistanceBetweenPoints(double x, double y, double x2, double y2) {
    return sqrt(pow(x - x2, 2) + pow(y - y2, 2));
}

extern int intInArray(float val, int *arr, size_t n) {
    for(size_t i = 0; i < n; i++) {
        if(arr[i] == val)
            return 1;
    }
    return 0;
}


double getDifference(double first, double second) {
    return fabs(first - second);
}


int rectCollidesWithRect(double firstX, double firstY, double firstWidth, double firstHeight, double secondX, double secondY, double secondWidth, double secondHeight) {
    // Checks if two rectangles are checking each other.
    if (firstX + firstWidth <= secondX) {
        return 0;
    }  
    if (firstX >= secondX + secondWidth) {
        return 0;
    }
    if (firstY + firstHeight <= secondY) {
        return 0;
    }
    if (firstY >= secondY + secondHeight) {
        return 0;
    }
    return 1;
}


extern int pointCollidesWithRect(double pointX, double pointY, double x, double y, double width, double height) {
    double right = x + width;
    double top = y + height;
    // This just check if a single point collides with a rectangle.
    if (pointX > right) {
        return 0;
    }
    if (pointX < x) {
        return 0;
    }
    if (pointY > top) {
        return 0;
    }
    if (pointY < y) {
        return 0;
    }
    return 1;
}





double* handleCollisionWithStaticRect(double xVelocity, double yVelocity, double firstX, double firstY, double firstWidth, double firstHeight, double rectX, double rectY, double rectWidth, double rectHeight) {
    double *attrs = malloc(sizeof(double) * 5);
    double firstRight = firstX + firstWidth; double firstTop = firstY + firstHeight;
    double rectRight = rectX + rectWidth; double rectTop = rectY + rectHeight;
    double *intersection;
    // This is the rectangle created by two collisions, the amount of x intersection and the amount of y intersection. 
    intersection = getIntersectionOfRects(firstX, firstY, firstWidth, firstHeight, rectX, rectY, rectWidth, rectHeight);

    // We don't want to do anything if the rectangles aren't colliding, and if there is no intersection between the two then they aren't colliding.
    if (!(intersection[0] == 0) && !(intersection[1] == 0)) {
        attrs[4] = 1;
        // We modify the axis with the least intersection, so if the width of this rectangle is less than the height, we modify the x position.
        if (intersection[0] <= intersection[1]) {
            // The intersection is never negative, so we check which direction we are moving and modify the position based on that.
            // I don't think this solution would work if the other rect was moving.
            if (xVelocity >= 0) {
                // We separate the rect from the static rect.
                firstX -= intersection[0];
            }   
            else {
                firstX += intersection[0];
            }
            xVelocity = 0;
        }
        else {
            if (yVelocity >= 0) {
                firstY -= intersection[1];
            }   
            else {
                firstY += intersection[1];
            }
            yVelocity = 0;
        }
    }
    else {
        attrs[4] = 0;
    }

    // We use this attrs variable so we don't have to do multiple function calls on the Python side and the code is cleaner. 
    attrs[0] = firstX; attrs[1] = firstY; attrs[2] = xVelocity; attrs[3] = yVelocity;
    return attrs;
}


double* handleCollisionsWithStaticRects(double *attrs, double width, double height, struct rectList rects) {
    // This function solves collisions with a list of rectangles.
    struct rect rect;
    
    double area = 0, biggestArea = 1;
    struct rect biggestRect;
    // Iterate until there is no collisions. 
    while (biggestArea > 0) {
        biggestArea = 0;

        // Loop through all the neighboring tiles and get their intersections, with that information we figure out tile with the biggest intersection.
        for (int i = 0; i < rects.length; i++) {
            rect = rects.rects[i];
            // This is the rectangle created by two collisions, the amount of x intersection and the amount of y intersection.
            double *intersection = getIntersectionOfRects(attrs[0], attrs[1], width, height, rect.x, rect.y, rect.width, rect.height);
            area = intersection[0] * intersection[1];

            // If the new area is bigger than the previously largest area, change the variables.
            if (area >= biggestArea) {
                biggestArea = area;
                biggestRect = rect;
            }
        }

        // If there is an intersection, solve it.
        if (biggestArea != 0) {
            attrs = handleCollisionWithStaticRect(attrs[2], attrs[3], attrs[0], attrs[1], width, height, biggestRect.x, biggestRect.y, biggestRect.width, biggestRect.height);
        }
    }

    return attrs;
}

// Keeping this here temporarily for enemies only, there is issues with them following a path to their destination which doesn't happen with this old method.
double* handleCollisionsWithStaticRectsOld(double *attrs, double width, double height, struct rectList rects) {
    // This function solves collisions with a list of rectangles.
    struct rect rect;
    double halfWidth = width / 2; double halfHeight = height / 2;
    for (int i = 0; i < rects.length; i++) {
        rect = rects.rects[i];
        if (pointCollidesWithRect(attrs[0], attrs[1] + halfHeight, rect.x, rect.y, rect.width, rect.height)) {
            attrs[0] = rect.x + rect.width;
            attrs[2] = 0;
            attrs[4] = 1;
        }

        if (pointCollidesWithRect(attrs[0] + width , attrs[1] + halfHeight, rect.x, rect.y, rect.width, rect.height)) {
            attrs[0] = rect.x - width;
            attrs[2] = 0;
            attrs[4] = 1;
        }
        if (pointCollidesWithRect(attrs[0] + halfWidth, attrs[1], rect.x, rect.y, rect.width, rect.height)) {
            attrs[1] = rect.y + rect.height;
            attrs[3] = 0;
            attrs[4] = 1;
        }
        if (pointCollidesWithRect(attrs[0] + halfWidth, attrs[1] + height, rect.x, rect.y, rect.width, rect.height)) {
            attrs[1] = rect.y - height;
            attrs[3] = 0;
            attrs[4] = 1;
        }
    }

    return attrs;
}


double* handleMapObjectCollisions(double xVelocity, double yVelocity, double x, double y, double width, double height, int oldCollisions) { 
    // This function handles collisions with tiles, the generator, and eventually some more things.
    // We use this attrs variable so python can get all the variables as a list, if we do that, we don't have to call more than one function.
    double *attrs = malloc(sizeof(double) * 5);
    double halfWidth = width / 2; double halfHeight = height / 2;
    double area = 0, biggestArea = 1, centerX = x + halfWidth, centerY = y + halfHeight;
    double *intersection;
    struct vec2dInt offset, pos;

    // This list is for all the stuff to check collisions with.
    struct rectList objects;
    objects.length = 0;
    // We allocate the maximum amount of space we'll need and then shorten the list to the needed amount later. IT LOOKS NICER OKAY?!
    objects.rects = malloc(sizeof(struct rect) * 9);

    // Add all the solid adjacent tiles to the objects list but as a rect struct.
    for (int i = 0; i < 8; i++) {
        pos.x = (int)(centerX + adjacentPositionOffsetList[i][0]);
        pos.y = (int)(centerY + adjacentPositionOffsetList[i][1]);
        if (!inMap(pos.x, pos.y)) {
            continue; 
        }
        
        if (tiles[pos.y][pos.x].solid) {
            objects.rects[objects.length].width = 1;
            objects.rects[objects.length].height = 1;
            objects.rects[objects.length].x = pos.x;
            objects.rects[objects.length].y = pos.y;
            objects.length += 1;
        }
    }
    
    // Shorten the list with realloc.
    objects.rects = realloc(objects.rects, sizeof(struct rect) * objects.length);

    // Map the items of the list to the variables.
    attrs[0] = x; attrs[1] = y; attrs[2] = xVelocity; attrs[3] = yVelocity; attrs[4] = 0;

    if (!oldCollisions) {
        // Solve collisions with all objects in the objects list.
        attrs = handleCollisionsWithStaticRects(attrs, width, height, objects);
    }
    else {
        // Solve collisions with all objects in the objects list.
        attrs = handleCollisionsWithStaticRectsOld(attrs, width, height, objects); 
    }

    free(objects.rects);

    return attrs;
}
